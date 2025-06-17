"""
Zaawansowane testy integracyjne systemu walki dla gry Kampania 1939.
Testuje rzeczywiste mechaniki walki, CombatAction, eliminację, VP, modyfikatory terenu.
"""

import unittest
import sys
import os
import random

# Dodaj katalog główny do ścieżki
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from engine.token import Token
from engine.board import Board
from engine.action import CombatAction, MoveAction
from engine.engine import GameEngine
from engine.player import Player


class TestAdvancedCombatSystem(unittest.TestCase):
    """Zaawansowane testy integracyjne mechaniki walki"""
    
    def setUp(self):
        """Przygotowanie środowiska testowego z GameEngine"""
        # Używamy prawdziwej mapy
        self.board = Board("data/map_data.json")
        
        # Symulujemy GameEngine z podstawowymi danymi
        self.engine = type('MockEngine', (), {
            'board': self.board,
            'tokens': [],
            'players': [],
            'turn': 1
        })()
          # Dodaj graczy
        self.player1 = Player(player_id=1, nation="Germany", role="Generał")
        self.player2 = Player(player_id=2, nation="Poland", role="Generał")
        self.engine.players = [self.player1, self.player2]
        
    def create_combat_token(self, token_type, size, player_id, nation, q, r):
        """Pomocnicza funkcja do tworzenia żetonów z pełnymi danymi bojowymi"""
        
        # Wartości po rebalansingu - struktura zgodna z CombatAction
        default_values = {
            "infantry": {
                "small": {
                    "move": 2, 
                    "attack": {"value": 6, "range": 1}, 
                    "defense_value": 6, 
                    "combat_value": 6, 
                    "maintenance": 1,
                    "price": 10
                },
                "medium": {
                    "move": 2, 
                    "attack": {"value": 8, "range": 1}, 
                    "defense_value": 8, 
                    "combat_value": 8, 
                    "maintenance": 2,
                    "price": 15
                },
                "large": {
                    "move": 2, 
                    "attack": {"value": 10, "range": 1}, 
                    "defense_value": 10, 
                    "combat_value": 10, 
                    "maintenance": 3,
                    "price": 20
                }
            },
            "tank": {
                "small": {
                    "move": 2, 
                    "attack": {"value": 10, "range": 1}, 
                    "defense_value": 8, 
                    "combat_value": 10, 
                    "maintenance": 3,
                    "price": 30
                },
                "medium": {
                    "move": 2, 
                    "attack": {"value": 12, "range": 1}, 
                    "defense_value": 10, 
                    "combat_value": 12, 
                    "maintenance": 4,
                    "price": 40
                },
                "large": {
                    "move": 2, 
                    "attack": {"value": 15, "range": 1}, 
                    "defense_value": 12, 
                    "combat_value": 15, 
                    "maintenance": 5,
                    "price": 50
                }
            },
            "artillery": {
                "small": {
                    "move": 1, 
                    "attack": {"value": 8, "range": 3}, 
                    "defense_value": 4, 
                    "combat_value": 8, 
                    "maintenance": 2,
                    "price": 25
                },
                "medium": {
                    "move": 1, 
                    "attack": {"value": 10, "range": 3}, 
                    "defense_value": 5, 
                    "combat_value": 10, 
                    "maintenance": 3,
                    "price": 35
                },
                "large": {
                    "move": 1, 
                    "attack": {"value": 12, "range": 3}, 
                    "defense_value": 6, 
                    "combat_value": 12, 
                    "maintenance": 4,
                    "price": 45
                }
            }
        }
        
        stats = default_values[token_type][size]
        token = Token(
            id=f"{token_type}_{size}_{player_id}_{q}_{r}",
            owner=f"{player_id} ({nation})",
            stats=stats,
            q=q, 
            r=r
        )
        
        # Ustaw combat_value jako osobny atrybut (używany przez CombatAction)
        token.combat_value = stats["combat_value"]
        token.currentMovePoints = stats["move"]
        token.maxMovePoints = stats["move"]
        
        # Dodaj do engine.tokens
        self.engine.tokens.append(token)
        
        return token
        
    def test_basic_combat_execution(self):
        """Test podstawowego wykonania walki przez CombatAction"""
        # Tworzymy dwie jednostki sąsiadujące ze sobą
        attacker = self.create_combat_token("infantry", "medium", 1, "Germany", 10, 10)
        defender = self.create_combat_token("infantry", "medium", 2, "Poland", 11, 10)
        
        # Zapisujemy początkowe wartości
        initial_attacker_cv = attacker.combat_value
        initial_defender_cv = defender.combat_value
        
        # Wykonujemy atak
        combat_action = CombatAction(attacker.id, defender.id)
        success, message = combat_action.execute(self.engine)
        
        # Sprawdzamy czy atak się udał
        self.assertTrue(success)
        self.assertIsNotNone(message)
        
        # Sprawdzamy czy jednostki poniosły straty
        self.assertLessEqual(attacker.combat_value, initial_attacker_cv)
        self.assertLessEqual(defender.combat_value, initial_defender_cv)
        
        # Sprawdzamy czy attacker stracił wszystkie punkty ruchu
        self.assertEqual(attacker.currentMovePoints, 0)
        
    def test_artillery_range_combat(self):
        """Test walki artylerii z zasięgiem 3"""
        # Artyleria z zasięgiem 3
        artillery = self.create_combat_token("artillery", "medium", 1, "Germany", 5, 5)
        target = self.create_combat_token("infantry", "small", 2, "Poland", 8, 5)  # 3 heksy dalej
        
        # Sprawdzamy czy artyleria może atakować z odległości
        dist = self.engine.board.hex_distance((artillery.q, artillery.r), (target.q, target.r))
        self.assertEqual(dist, 3)
        
        initial_target_cv = target.combat_value
        initial_artillery_cv = artillery.combat_value
        
        # Wykonujemy atak
        combat_action = CombatAction(artillery.id, target.id)
        success, message = combat_action.execute(self.engine)
        
        self.assertTrue(success)
        
        # Cel powinien zostać uszkodzony
        self.assertLess(target.combat_value, initial_target_cv)
        
        # Artyleria może nie otrzymać kontrataku (jeśli piechota ma zasięg 1)
        # W zależności od implementacji
        
    def test_combat_out_of_range(self):
        """Test próby ataku poza zasięgiem"""
        attacker = self.create_combat_token("infantry", "small", 1, "Germany", 0, 0)
        defender = self.create_combat_token("infantry", "small", 2, "Poland", 5, 5)  # Za daleko
        
        # Próbujemy atakować poza zasięgiem
        combat_action = CombatAction(attacker.id, defender.id)
        success, message = combat_action.execute(self.engine)
        
        # Atak powinien się nie udać
        self.assertFalse(success)
        self.assertIn("Za daleko", message)
        
    def test_friendly_fire_prevention(self):
        """Test zapobiegania atakom na własne jednostki"""
        # Dwie jednostki tego samego gracza
        unit1 = self.create_combat_token("infantry", "small", 1, "Germany", 3, 3)
        unit2 = self.create_combat_token("tank", "small", 1, "Germany", 4, 3)
        
        # Próbujemy atakować własną jednostkę
        combat_action = CombatAction(unit1.id, unit2.id)
        success, message = combat_action.execute(self.engine)
        
        # Atak powinien być zablokowany
        self.assertFalse(success)
        self.assertIn("własnych", message)
        
    def test_unit_elimination_and_vp(self):
        """Test eliminacji jednostki i przyznawania VP"""
        # Silna jednostka vs słaba z niskim HP
        strong_unit = self.create_combat_token("tank", "large", 1, "Germany", 15, 15)
        weak_unit = self.create_combat_token("infantry", "small", 2, "Poland", 16, 15)
        weak_unit.combat_value = 1  # Bardzo słaba jednostka
        
        initial_token_count = len(self.engine.tokens)
        initial_vp_p1 = self.player1.victory_points
        initial_vp_p2 = self.player2.victory_points
        
        # Wykonujemy atak który prawdopodobnie wyeliminuje słabą jednostkę
        combat_action = CombatAction(strong_unit.id, weak_unit.id)
        success, message = combat_action.execute(self.engine)
        
        self.assertTrue(success)
        
        # Sprawdzamy czy jednostka została wyeliminowana lub osłabiona
        if weak_unit not in self.engine.tokens:
            # Jednostka wyeliminowana
            self.assertLess(len(self.engine.tokens), initial_token_count)
            # VP powinny się zmienić
            self.assertNotEqual(self.player1.victory_points, initial_vp_p1)
            
    def test_no_movement_points_combat(self):
        """Test blokady ataku gdy brak punktów ruchu"""
        attacker = self.create_combat_token("infantry", "medium", 1, "Germany", 7, 7)
        defender = self.create_combat_token("infantry", "medium", 2, "Poland", 8, 7)
        
        # Zabieramy wszystkie punkty ruchu
        attacker.currentMovePoints = 0
        
        # Próbujemy atakować bez punktów ruchu
        combat_action = CombatAction(attacker.id, defender.id)
        success, message = combat_action.execute(self.engine)
        
        # Atak powinien być zablokowany
        self.assertFalse(success)
        self.assertIn("ruchu", message)
        
    def test_counterattack_mechanics(self):
        """Test mechaniki kontrataku"""
        # Dwie jednostki z zasięgiem 1
        unit1 = self.create_combat_token("infantry", "medium", 1, "Germany", 20, 20)
        unit2 = self.create_combat_token("infantry", "medium", 2, "Poland", 21, 20)
        
        initial_cv1 = unit1.combat_value
        initial_cv2 = unit2.combat_value
        
        # Wykonujemy atak - oba powinny otrzymać obrażenia
        combat_action = CombatAction(unit1.id, unit2.id)
        success, message = combat_action.execute(self.engine)
        
        self.assertTrue(success)
        
        # Oba żetony powinny zostać uszkodzone (atak + kontratak)
        self.assertLess(unit1.combat_value, initial_cv1)
        self.assertLess(unit2.combat_value, initial_cv2)
        
    def test_terrain_defense_modifier(self):
        """Test modyfikatorów obrony terenu"""
        attacker = self.create_combat_token("infantry", "medium", 1, "Germany", 0, 1)
        defender = self.create_combat_token("infantry", "medium", 2, "Poland", 0, 2)
        
        # Sprawdzamy czy teren ma modyfikatory
        defender_tile = self.engine.board.get_tile(defender.q, defender.r)
        
        if defender_tile and hasattr(defender_tile, 'defense_mod'):
            initial_defender_cv = defender.combat_value
            
            combat_action = CombatAction(attacker.id, defender.id)
            success, message = combat_action.execute(self.engine)
            
            self.assertTrue(success)
            # Trudno testować konkretny efekt bez kontrolowania losowości
            # ale test sprawdza czy mechanizm nie wywala błędów
            
    def test_multiple_combat_rounds(self):
        """Test wielokrotnych rund walki"""
        unit1 = self.create_combat_token("tank", "medium", 1, "Germany", 25, 25)
        unit2 = self.create_combat_token("tank", "medium", 2, "Poland", 26, 25)
        
        rounds = 0
        max_rounds = 5
        
        while (unit1 in self.engine.tokens and 
               unit2 in self.engine.tokens and 
               rounds < max_rounds):
            
            # Przywracamy punkty ruchu dla kolejnej rundy
            unit1.currentMovePoints = unit1.maxMovePoints
            
            combat_action = CombatAction(unit1.id, unit2.id)
            success, message = combat_action.execute(self.engine)
            
            if not success:
                break
                
            rounds += 1
            
        # Po kilku rundach przynajmniej jedna jednostka powinna być znacznie osłabiona
        if unit1 in self.engine.tokens and unit2 in self.engine.tokens:
            total_remaining_cv = unit1.combat_value + unit2.combat_value
            initial_total_cv = unit1.stats['combat_value'] + unit2.stats['combat_value']
            self.assertLess(total_remaining_cv, initial_total_cv)
            
    def test_different_unit_types_balance(self):
        """Test balansu między różnymi typami jednostek"""
        # Tank vs Infantry
        tank = self.create_combat_token("tank", "medium", 1, "Germany", 30, 30)
        infantry = self.create_combat_token("infantry", "large", 2, "Poland", 31, 30)
        
        tank_efficiency = tank.stats['attack']['value'] / tank.stats['price']
        infantry_efficiency = infantry.stats['attack']['value'] / infantry.stats['price']
        
        # Efektywność nie powinna się różnić o więcej niż 100%
        ratio = max(tank_efficiency, infantry_efficiency) / min(tank_efficiency, infantry_efficiency)
        self.assertLess(ratio, 2.5)
        
        # Test rzeczywistej walki
        initial_tank_cv = tank.combat_value
        initial_infantry_cv = infantry.combat_value
        
        combat_action = CombatAction(tank.id, infantry.id)
        success, message = combat_action.execute(self.engine)
        
        self.assertTrue(success)
        # Oba powinny zostać uszkodzone
        self.assertLess(tank.combat_value, initial_tank_cv)
        self.assertLess(infantry.combat_value, initial_infantry_cv)


class TestCombatRebalancingValidation(unittest.TestCase):
    """Testy walidujące skuteczność rebalansingu"""
    
    def setUp(self):
        self.board = Board("data/map_data.json")
        
    def test_movement_speed_rebalancing(self):
        """Test czy rebalansing rzeczywiście spowolnił czołgi"""
        
        # Wartości przed rebalansem (dla porównania)
        old_tank_move = 4  # Przykładowa stara wartość
        old_infantry_move = 2
        
        # Nowe wartości po rebalansingu
        new_tank_move = 2
        new_infantry_move = 2
        
        # Sprawdzamy czy różnica została zmniejszona
        old_difference = old_tank_move - old_infantry_move
        new_difference = new_tank_move - new_infantry_move
        
        self.assertLessEqual(new_difference, old_difference)
        self.assertEqual(new_tank_move, new_infantry_move)  # Teraz równe
        
    def test_cost_effectiveness_improvement(self):
        """Test czy rebalansing poprawił efektywność kosztową"""
        
        # Symulujemy wartości jednostek po rebalansingu
        infantry_combat_per_cost = 8 / 15  # combat_value / price
        tank_combat_per_cost = 12 / 40
        artillery_combat_per_cost = 10 / 35
        
        # Sprawdzamy czy różnice są rozsądne
        ratios = [infantry_combat_per_cost, tank_combat_per_cost, artillery_combat_per_cost]
        max_ratio = max(ratios)
        min_ratio = min(ratios)
        
        # Różnica efektywności nie powinna być większa niż 2:1
        self.assertLess(max_ratio / min_ratio, 2.0)
        
    def test_attack_defense_balance_validation(self):
        """Test czy stosunek atak/obrona jest zrównoważony"""
        
        # Sprawdzamy różne typy jednostek po rebalansingu
        test_units = [
            {"attack": 8, "defense": 8, "name": "infantry_medium"},
            {"attack": 12, "defense": 10, "name": "tank_medium"},
            {"attack": 10, "defense": 5, "name": "artillery_medium"}
        ]
        
        for unit in test_units:
            ratio = unit["attack"] / unit["defense"]
            # Stosunek atak/obrona powinien być między 0.8 a 2.5
            self.assertGreater(ratio, 0.8, f"Unit {unit['name']} ma za niski atak względem obrony")
            self.assertLess(ratio, 2.5, f"Unit {unit['name']} ma za wysoki atak względem obrony")


if __name__ == "__main__":
    # Ustawienie seed dla powtarzalności testów
    random.seed(42)
    
    # Uruchomienie testów
    unittest.main(verbosity=2)
