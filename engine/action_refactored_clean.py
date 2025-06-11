# -*- coding: utf-8 -*-
"""
Refaktoryzowane akcje - czysta architektura
Podział na mniejsze, testowalne komponenty
"""

from typing import Tuple, Optional, Dict, Any, List, Set
from dataclasses import dataclass


@dataclass
class ActionResult:
    """Wynik wykonania akcji"""
    success: bool
    message: str
    data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}


class BaseAction:
    """Bazowa klasa dla wszystkich akcji"""
    
    def __init__(self, token_id: str):
        self.token_id = token_id
    
    def execute(self, engine) -> ActionResult:
        """Wykonaj akcję"""
        raise NotImplementedError("Każda akcja musi implementować execute!")
    
    def _find_token(self, engine, token_id: str):
        """Znajdź żeton po ID"""
        return next((t for t in engine.tokens if t.id == token_id), None)
    
    def _find_player_by_token(self, engine, token):
        """Znajdź gracza będącego właścicielem żetonu"""
        if not hasattr(token, 'owner'):
            return None
        
        for player in getattr(engine, 'players', []):
            if token.owner == f"{player.id} ({player.nation})":
                return player
        return None


class MovementValidator:
    """Walidator ruchu żetonów"""
    
    @staticmethod
    def validate_basic_movement(token, dest_q: int, dest_r: int, engine) -> Tuple[bool, str]:
        """Podstawowa walidacja ruchu"""
        if not token:
            return False, "Brak żetonu."
        
        tile = engine.board.get_tile(dest_q, dest_r)
        if tile is None:
            return False, "Brak pola docelowego."
        
        if tile.move_mod == -1:
            return False, "Pole nieprzejezdne."
        
        # Sprawdź czy pole nie jest zajęte przez sojusznika
        if engine.board.is_occupied(dest_q, dest_r):
            for t in engine.tokens:
                if t.q == dest_q and t.r == dest_r and t.owner == token.owner:
                    return False, "Pole zajęte przez sojusznika."
        
        return True, "OK"
    
    @staticmethod
    def validate_movement_resources(token) -> Tuple[bool, str]:
        """Sprawdź czy żeton ma wystarczające zasoby do ruchu"""
        # Przygotuj żeton do ruchu
        movement_mode = getattr(token, 'movement_mode', 'combat')
        token.apply_movement_mode()
        
        max_mp = token.currentMovePoints
        if not hasattr(token, 'maxMovePoints'):
            token.maxMovePoints = max_mp
        
        if not hasattr(token, 'maxFuel'):
            token.maxFuel = token.stats.get('maintenance', 0)
        
        if not hasattr(token, 'currentFuel'):
            token.currentFuel = token.maxFuel
        
        if token.currentMovePoints <= 0:
            return False, "Brak punktów ruchu."
        
        if token.currentFuel <= 0:
            return False, "Brak paliwa."
        
        return True, "OK"


class PathfindingService:
    """Serwis pathfindingu i obliczania kosztów ruchu"""
    
    @staticmethod
    def find_movement_path(engine, token, start: Tuple[int, int], goal: Tuple[int, int], player=None):
        """Znajdź ścieżkę ruchu z uwzględnieniem widzialności"""
        visible_tokens = None
        if player and hasattr(player, 'visible_tokens'):
            visible_tokens = set(player.visible_tokens)
        
        return engine.board.find_path(
            start, goal,
            max_mp=token.currentMovePoints,
            max_fuel=token.currentFuel,
            visible_tokens=visible_tokens
        )
    
    @staticmethod
    def calculate_path_cost_and_position(engine, token, path: List[Tuple[int, int]]) -> Tuple[int, int, Tuple[int, int]]:
        """Oblicz koszt ścieżki i końcową pozycję z uwzględnieniem przeciwników"""
        if not path or len(path) <= 1:
            return 0, 0, (token.q, token.r)
        
        path_cost = 0
        fuel_cost = 0
        final_pos = (token.q, token.r)
        sight = token.stats.get('sight', 0)
        
        for step in path[1:]:  # pomijamy start
            tile = engine.board.get_tile(*step)
            move_mod = getattr(tile, 'move_mod', 0)
            move_cost = 1 + move_mod
            
            # Sprawdź czy stać na ten krok
            if (token.currentMovePoints - (path_cost + move_cost) < 0 or 
                token.currentFuel - (fuel_cost + move_cost) < 0):
                break
            
            # Sprawdź czy w polu widzenia jest przeciwnik
            if PathfindingService._enemy_in_sight(engine, token, step, sight):
                final_pos = step
                path_cost += move_cost
                fuel_cost += move_cost
                break
            
            final_pos = step
            path_cost += move_cost
            fuel_cost += move_cost
        
        return path_cost, fuel_cost, final_pos
    
    @staticmethod
    def _enemy_in_sight(engine, token, position: Tuple[int, int], sight: int) -> bool:
        """Sprawdź czy w polu widzenia jest przeciwnik"""
        visible_hexes = VisionService.calculate_visible_hexes(engine.board, position, sight)
        
        for enemy_token in engine.tokens:
            if not hasattr(enemy_token, 'owner') or not hasattr(token, 'owner'):
                continue
            if not enemy_token.owner or not token.owner:
                continue
            
            if (enemy_token.q, enemy_token.r) in visible_hexes:
                enemy_nation = enemy_token.owner.split('(')[-1].replace(')', '').strip()
                token_nation = token.owner.split('(')[-1].replace(')', '').strip()
                if enemy_nation != token_nation:
                    return True
        
        return False


class VisionService:
    """Serwis zarządzania widzeniem i odkrywaniem mapy"""
    
    @staticmethod
    def calculate_visible_hexes(board, position: Tuple[int, int], sight: int) -> Set[Tuple[int, int]]:
        """Oblicz widzialne heksy z danej pozycji"""
        visible_hexes = set()
        q, r = position
        
        for dq in range(-sight, sight + 1):
            for dr in range(-sight, sight + 1):
                hex_q = q + dq
                hex_r = r + dr
                if board.hex_distance(position, (hex_q, hex_r)) <= sight:
                    if board.get_tile(hex_q, hex_r) is not None:
                        visible_hexes.add((hex_q, hex_r))
        
        return visible_hexes
    
    @staticmethod
    def update_player_vision(engine, player, token, path: List[Tuple[int, int]], final_pos: Tuple[int, int]):
        """Aktualizuj widzenie gracza na podstawie trasy ruchu"""
        if not player:
            return
        
        sight = token.stats.get('sight', 0)
        
        # Odkryj heksy na całej trasie do końcowej pozycji
        final_index = path.index(final_pos) if final_pos in path else len(path) - 1
        path_to_final = path[:final_index + 1]
        
        for hex_coords in path_to_final:
            visible_hexes = VisionService.calculate_visible_hexes(engine.board, hex_coords, sight)
            player.temp_visible_hexes.update(visible_hexes)
            
            # Dodaj żetony przeciwnika z widzialnych heksów
            VisionService._add_visible_enemy_tokens(engine, player, token, visible_hexes)
    
    @staticmethod
    def _add_visible_enemy_tokens(engine, player, token, visible_hexes: Set[Tuple[int, int]]):
        """Dodaj żetony przeciwnika z widzialnych heksów"""
        for hex_pos in visible_hexes:
            for enemy_token in engine.tokens:
                if ((enemy_token.q, enemy_token.r) == hex_pos and 
                    hasattr(enemy_token, 'owner') and hasattr(token, 'owner')):
                    
                    enemy_nation = enemy_token.owner.split('(')[-1].replace(')', '').strip()
                    token_nation = token.owner.split('(')[-1].replace(')', '').strip()
                    
                    if enemy_nation != token_nation:
                        player.temp_visible_tokens.add(enemy_token.id)


class MoveAction(BaseAction):
    """Akcja ruchu żetonu"""
    
    def __init__(self, token_id: str, dest_q: int, dest_r: int):
        super().__init__(token_id)
        self.dest_q = dest_q
        self.dest_r = dest_r
    
    def execute(self, engine) -> ActionResult:
        """Wykonaj ruch żetonu"""
        # Znajdź żeton i gracza
        token = self._find_token(engine, self.token_id)
        if not token:
            return ActionResult(False, "Brak żetonu.")
        
        player = self._find_player_by_token(engine, token)
        
        # Walidacja podstawowa
        valid, message = MovementValidator.validate_basic_movement(
            token, self.dest_q, self.dest_r, engine
        )
        if not valid:
            return ActionResult(False, message)
        
        # Walidacja zasobów
        valid, message = MovementValidator.validate_movement_resources(token)
        if not valid:
            return ActionResult(False, message)
        
        # Znajdź ścieżkę
        start = (token.q, token.r)
        goal = (self.dest_q, self.dest_r)
        path = PathfindingService.find_movement_path(engine, token, start, goal, player)
        
        if not path:
            return ActionResult(False, "Brak ścieżki do celu.")
        
        # Oblicz koszt i końcową pozycję
        path_cost, fuel_cost, final_pos = PathfindingService.calculate_path_cost_and_position(
            engine, token, path
        )
        
        if final_pos == start:
            return ActionResult(False, "Brak wystarczających punktów ruchu lub paliwa na ruch.")
        
        # Wykonaj ruch
        token.set_position(*final_pos)
        token.currentMovePoints -= path_cost
        token.currentFuel -= fuel_cost
        
        # Aktualizuj widzenie gracza
        VisionService.update_player_vision(engine, player, token, path, final_pos)
        
        return ActionResult(
            True, 
            "OK",
            {
                'final_position': final_pos,
                'path_cost': path_cost,
                'fuel_cost': fuel_cost,
                'remaining_mp': token.currentMovePoints,
                'remaining_fuel': token.currentFuel
            }
        )


class CombatCalculator:
    """Kalkulator wyników walki"""
    
    @staticmethod
    def calculate_combat_result(attacker, defender, engine) -> Dict[str, Any]:
        """Oblicz wynik walki między dwoma żetonami"""
        import random
        
        # Wartości ataku i obrony
        attack_val = attacker.stats.get('attack', {}).get('value', 0)
        defense_val = defender.stats.get('defense_value', 0)
        
        # Modyfikator terenu
        tile = engine.board.get_tile(defender.q, defender.r)
        defense_mod = tile.defense_mod if tile else 0
        defense_total = defense_val + defense_mod
        
        # Losowe modyfikatory
        attack_mult = random.uniform(0.8, 1.2)
        defense_mult = random.uniform(0.8, 1.2)
        
        # Wyniki
        attack_result = int(round(attack_val * attack_mult))
        defense_result = int(round(defense_total * defense_mult))
        
        # Sprawdź czy obrońca może kontratakować
        attack_range = attacker.stats.get('attack', {}).get('range', 1)
        defense_range = defender.stats.get('attack', {}).get('range', 1)
        distance = engine.board.hex_distance((attacker.q, attacker.r), (defender.q, defender.r))
        can_counterattack = distance <= defense_range
        
        if not can_counterattack:
            defense_result = 0
        
        return {
            'attack_result': attack_result,
            'defense_result': defense_result,
            'attack_mult': attack_mult,
            'defense_mult': defense_mult,
            'defense_mod': defense_mod,
            'can_counterattack': can_counterattack,
            'distance': distance,
            'attack_range': attack_range,
            'defense_range': defense_range
        }


class CombatResolver:
    """Resolver rozstrzygający walkę i jej konsekwencje"""
    
    @staticmethod
    def resolve_combat(engine, attacker, defender, combat_result: Dict[str, Any]) -> str:
        """Rozstrzygnij walkę i zwróć komunikat"""
        attack_damage = combat_result['attack_result']
        defense_damage = combat_result['defense_result']
        
        # Zadaj obrażenia
        defender.combat_value = max(0, getattr(defender, 'combat_value', 0) - attack_damage)
        attacker.combat_value = max(0, getattr(attacker, 'combat_value', 0) - defense_damage)
        
        messages = []
        
        # Sprawdź eliminację obrońcy
        if defender.combat_value <= 0:
            defender_msg = CombatResolver._handle_defender_elimination(engine, attacker, defender)
            messages.append(defender_msg)
        else:
            messages.append(f"Obrońca stracił {attack_damage} punktów, pozostało: {defender.combat_value}")
        
        # Sprawdź eliminację atakującego
        if attacker.combat_value <= 0:
            CombatResolver._award_vp_for_elimination(engine, defender, attacker)
            engine.tokens.remove(attacker)
            messages.append("Atakujący został zniszczony!")
        else:
            if defense_damage > 0:
                messages.append(f"Atakujący stracił {defense_damage} punktów, pozostało: {attacker.combat_value}")
        
        return "\n".join(messages)
    
    @staticmethod
    def _handle_defender_elimination(engine, attacker, defender) -> str:
        """Obsłuż eliminację obrońcy"""
        import random
        
        # 50% szans na przeżycie i odwrót
        if random.random() < 0.5:
            retreat_pos = CombatResolver._find_retreat_position(engine, attacker, defender)
            if retreat_pos:
                defender.combat_value = 1
                defender.set_position(*retreat_pos)
                return f"Obrońca przeżył z 1 punktem i cofnął się na {retreat_pos}!"
        
        # Obrońca ginie
        CombatResolver._award_vp_for_elimination(engine, attacker, defender)
        engine.tokens.remove(defender)
        return "Obrońca został zniszczony!"
    
    @staticmethod
    def _find_retreat_position(engine, attacker, defender) -> Optional[Tuple[int, int]]:
        """Znajdź pozycję do odwrotu"""
        from engine.hex_utils import get_neighbors
        
        neighbors = get_neighbors(defender.q, defender.r)
        start_dist = engine.board.hex_distance((attacker.q, attacker.r), (defender.q, defender.r))
        
        for nq, nr in neighbors:
            # Pole musi istnieć i być wolne
            if not engine.board.get_tile(nq, nr):
                continue
            if engine.board.is_occupied(nq, nr):
                continue
            
            # Pole musi oddalać od atakującego
            if engine.board.hex_distance((attacker.q, attacker.r), (nq, nr)) > start_dist:
                return (nq, nr)
        
        return None
    
    @staticmethod
    def _award_vp_for_elimination(engine, winner_token, loser_token):
        """Przyznaj VP za eliminację żetonu"""
        # Znajdź graczy
        winner_player = None
        loser_player = None
        
        for player in getattr(engine, 'players', []):
            if hasattr(winner_token, 'owner') and winner_token.owner == f"{player.id} ({player.nation})":
                winner_player = player
            if hasattr(loser_token, 'owner') and loser_token.owner == f"{player.id} ({player.nation})":
                loser_player = player
        
        price = loser_token.stats.get('price', 0)
        
        # Dodaj punkty zwycięzcy
        if winner_player:
            winner_player.victory_points += price
            winner_player.vp_history.append({
                'turn': getattr(engine, 'turn', None),
                'amount': price,
                'reason': 'eliminacja',
                'token_id': loser_token.id,
                'enemy': loser_token.owner
            })
        
        # Odejmij punkty przegranemu
        if loser_player:
            loser_player.victory_points -= price
            loser_player.vp_history.append({
                'turn': getattr(engine, 'turn', None),
                'amount': -price,
                'reason': 'utrata',
                'token_id': loser_token.id,
                'enemy': winner_token.owner
            })


class CombatAction(BaseAction):
    """Akcja walki między żetonami"""
    
    def __init__(self, attacker_id: str, defender_id: str):
        super().__init__(attacker_id)
        self.defender_id = defender_id
    
    def execute(self, engine) -> ActionResult:
        """Wykonaj walkę"""
        # Znajdź żetony
        attacker = self._find_token(engine, self.token_id)
        defender = self._find_token(engine, self.defender_id)
        
        if not attacker or not defender:
            return ActionResult(False, "Brak żetonu atakującego lub broniącego.")
        
        # Walidacja walki
        valid, message = self._validate_combat(engine, attacker, defender)
        if not valid:
            return ActionResult(False, message)
        
        # Zużyj punkty ruchu atakującego
        attacker.currentMovePoints = 0
        
        # Oblicz wynik walki
        combat_result = CombatCalculator.calculate_combat_result(attacker, defender, engine)
        
        # Wyświetl debug walki
        self._print_combat_debug(attacker, defender, combat_result)
        
        # Rozstrzygnij walkę
        result_message = CombatResolver.resolve_combat(engine, attacker, defender, combat_result)
        
        return ActionResult(
            True, 
            result_message,
            {
                'combat_result': combat_result,
                'attacker_remaining': getattr(attacker, 'combat_value', 0) if attacker in engine.tokens else 0,
                'defender_remaining': getattr(defender, 'combat_value', 0) if defender in engine.tokens else 0
            }
        )
    
    def _validate_combat(self, engine, attacker, defender) -> Tuple[bool, str]:
        """Waliduj możliwość przeprowadzenia walki"""
        # Sprawdź dystans
        attack_range = attacker.stats.get('attack', {}).get('range', 1)
        distance = engine.board.hex_distance((attacker.q, attacker.r), (defender.q, defender.r))
        
        if distance > attack_range:
            return False, f"Za daleko do ataku (zasięg: {attack_range})."
        
        # Sprawdź punkty ruchu
        if getattr(attacker, 'currentMovePoints', 0) <= 0:
            return False, "Brak punktów ruchu do ataku."
        
        # Sprawdź czy nie atakuje siebie
        if attacker.owner == defender.owner:
            return False, "Nie można atakować własnych żetonów!"
        
        return True, "OK"
    
    def _print_combat_debug(self, attacker, defender, combat_result: Dict[str, Any]):
        """Wyświetl informacje debugowe o walce"""
        print(f"[WALKA] Atakujący: {attacker.id} ({getattr(attacker, 'name', '')}) na {attacker.q},{attacker.r}")
        print(f"  Obrońca: {defender.id} ({getattr(defender, 'name', '')}) na {defender.q},{defender.r}")
        print(f"  Zasięg ataku: {combat_result['attack_range']}, dystans: {combat_result['distance']}")
        print(f"  Zasięg ataku obrońcy: {combat_result['defense_range']}")
        
        if not combat_result['can_counterattack']:
            print("  Obrońca nie może kontratakować (za mały zasięg) – atak jednostronny.")
        else:
            print("  Obrońca kontratakuje!")
        
        attack_val = attacker.stats.get('attack', {}).get('value', 0)
        defense_val = defender.stats.get('defense_value', 0)
        
        print(f"  Atak: {attack_val} x {combat_result['attack_mult']:.2f} = {combat_result['attack_result']}")
        print(f"  Obrona: {defense_val} + modyfikator terenu {combat_result['defense_mod']} "
              f"x {combat_result['defense_mult']:.2f} = {combat_result['defense_result']}")
        print(f"  Straty: obrońca -{combat_result['attack_result']}, atakujący -{combat_result['defense_result']}")


# Dla zgodności wstecznej - stare klasy Action
class Action:
    """Stara klasa Action dla zgodności wstecznej"""
    def __init__(self, token_id):
        self.token_id = token_id

    def execute(self, engine):
        raise NotImplementedError("Każda akcja musi implementować execute!")
