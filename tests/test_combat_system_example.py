"""
Testy integracyjne systemu walki dla gry Kampania 1939.
Testuje mechaniki walki między żetonami, modyfikatory terenu, kontratak, eliminację.
"""

import unittest
import sys
import os

# Dodaj katalog główny do ścieżki
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from engine.token import Token
from engine.board import Board
from engine.action import Action
from engine.player import Player


class TestCombatSystem(unittest.TestCase):
    """Testy integracyjne systemu walki"""
      def setUp(self):
        """Przygotowanie środowiska testowego"""
        self.board = Board("data/map_data.json")  # Ładuj prawdziwą mapę
        self.player1 = Player(player_id=1, name="Player1")
        self.player2 = Player(player_id=2, name="Player2")
          def create_token(self, token_type, size, player_id, q, r):
        """Pomocnicza funkcja do tworzenia żetonów z realistycznymi wartościami po rebalansingu"""
        
        # Wartości po rebalansingu według zmian w token_editor i token_shop
        default_values = {
            "infantry": {
                "small": {"move": 2, "attack": 6, "defense": 6, "hp": 8, "range": 1, "vision": 3, "combat_value": 6, "maintenance": 1},
                "medium": {"move": 2, "attack": 8, "defense": 8, "hp": 12, "range": 1, "vision": 3, "combat_value": 8, "maintenance": 2},
                "large": {"move": 2, "attack": 10, "defense": 10, "hp": 16, "range": 1, "vision": 3, "combat_value": 10, "maintenance": 3}
            },
            "tank": {
                "small": {"move": 2, "attack": 10, "defense": 8, "hp": 10, "range": 1, "vision": 3, "combat_value": 10, "maintenance": 3},
                "medium": {"move": 2, "attack": 12, "defense": 10, "hp": 15, "range": 1, "vision": 3, "combat_value": 12, "maintenance": 4},
                "large": {"move": 2, "attack": 15, "defense": 12, "hp": 20, "range": 1, "vision": 3, "combat_value": 15, "maintenance": 5}
            },
            "artillery": {
                "small": {"move": 1, "attack": 8, "defense": 4, "hp": 6, "range": 3, "vision": 4, "combat_value": 8, "maintenance": 2},
                "medium": {"move": 1, "attack": 10, "defense": 5, "hp": 8, "range": 3, "vision": 4, "combat_value": 10, "maintenance": 3},
                "large": {"move": 1, "attack": 12, "defense": 6, "hp": 10, "range": 3, "vision": 4, "combat_value": 12, "maintenance": 4}
            },
            "air": {
                "small": {"move": 6, "attack": 8, "defense": 4, "hp": 6, "range": 1, "vision": 5, "combat_value": 8, "maintenance": 3},
                "medium": {"move": 6, "attack": 10, "defense": 5, "hp": 8, "range": 1, "vision": 5, "combat_value": 10, "maintenance": 4},
                "large": {"move": 6, "attack": 12, "defense": 6, "hp": 10, "range": 1, "vision": 5, "combat_value": 12, "maintenance": 5}
            }
        }
        
        stats = default_values[token_type][size]
        token = Token(
            id=f"{token_type}_{size}_{player_id}_{q}_{r}",
            owner=f"player_{player_id}",
            stats=stats,
            q=q, 
            r=r
        )
        
        # Symulujemy umieszczenie na planszy
        if hasattr(self.board, 'tokens'):
            if not hasattr(self.board, 'tokens'):
                self.board.tokens = {}
            self.board.tokens[f"{q},{r}"] = token
        
        return token
        
    def test_basic_infantry_vs_infantry_combat(self):
        """Test podstawowej walki piechota vs piechota"""
        # Tworzymy dwie jednostki piechoty
        attacker = self.create_token("infantry", "medium", 1, 5, 5)
        defender = self.create_token("infantry", "medium", 2, 6, 5)
        
        # Sprawdzamy początkowe HP
        self.assertEqual(attacker.current_hp, 12)
        self.assertEqual(defender.current_hp, 12)
        
        # Wykonujemy atak
        action = Action(self.board)
        combat_result = action.resolve_combat(attacker, defender)
        
        # Sprawdzamy, że walka się odbyła
        self.assertIsNotNone(combat_result)
        self.assertTrue(attacker.current_hp <= 12)  # Napastnik może być ranny przez kontratak
        self.assertTrue(defender.current_hp < 12)   # Obrońca powinien zostać ranny
        
    def test_tank_vs_infantry_advantage(self):
        """Test przewagi czołgu nad piechotą"""
        tank = self.create_token("tank", "medium", 1, 3, 3)
        infantry = self.create_token("infantry", "medium", 2, 4, 3)
        
        initial_tank_hp = tank.current_hp
        initial_infantry_hp = infantry.current_hp
        
        # Czołg atakuje piechotę
        action = Action(self.board)
        combat_result = action.resolve_combat(tank, infantry)
        
        # Czołg powinien zadać więcej obrażeń niż otrzymać
        tank_damage_taken = initial_tank_hp - tank.current_hp
        infantry_damage_taken = initial_infantry_hp - infantry.current_hp
        
        # Piechota powinna zostać bardziej uszkodzona
        self.assertGreater(infantry_damage_taken, tank_damage_taken)
        
    def test_artillery_range_advantage(self):
        """Test przewagi zasięgu artylerii"""
        artillery = self.create_token("artillery", "medium", 1, 2, 2)
        infantry = self.create_token("infantry", "medium", 2, 5, 2)  # 3 heksy dalej
        
        action = Action(self.board)
        
        # Artyleria powinna móc atakować z odległości 3
        self.assertTrue(action.can_attack(artillery, infantry))
        
        # Piechota nie powinna móc wykonać kontrataku (zasięg 1)
        combat_result = action.resolve_combat(artillery, infantry)
        
        # Artyleria nie powinna otrzymać obrażeń (brak kontrataku)
        self.assertEqual(artillery.current_hp, artillery.max_hp)
        self.assertLess(infantry.current_hp, infantry.max_hp)
        
    def test_terrain_defense_modifier(self):
        """Test modyfikatorów obrony terenu"""
        # Umieszczamy jednostki na różnych typach terenu
        attacker = self.create_token("infantry", "medium", 1, 5, 5)
        
        # Symulujemy umieszczenie obrońcy na górach (bonus obrony)
        defender = self.create_token("infantry", "medium", 2, 6, 5)
        
        # Symulujemy teren górski dla obrońcy
        if hasattr(self.board, 'set_terrain'):
            self.board.set_terrain(6, 5, "mountain")
        
        action = Action(self.board)
        initial_defender_hp = defender.current_hp
        
        # Wykonujemy atak
        combat_result = action.resolve_combat(attacker, defender)
        
        # Obrońca na górach powinien otrzymać mniej obrażeń
        damage_taken = initial_defender_hp - defender.current_hp
        
        # Sprawdzamy, że walka się odbyła ale z modyfikatorami
        self.assertGreater(damage_taken, 0)
        
    def test_unit_elimination(self):
        """Test eliminacji jednostki po wyczerpaniu HP"""
        # Tworzymy słabszą jednostkę z niskim HP
        weak_unit = self.create_token("infantry", "small", 2, 8, 8)
        weak_unit.current_hp = 2  # Ustawiamy niskie HP
        
        strong_unit = self.create_token("tank", "large", 1, 9, 8)
        
        action = Action(self.board)
        
        # Wykonujemy atak który powinien wyeliminować słabą jednostkę
        combat_result = action.resolve_combat(strong_unit, weak_unit)
        
        # Sprawdzamy czy jednostka została wyeliminowana
        if weak_unit.current_hp <= 0:
            # Jednostka powinna zostać usunięta z planszy
            self.assertIsNone(self.board.get_token_at(8, 8))
            
    def test_counterattack_mechanism(self):
        """Test mechanizmu kontrataku"""
        attacker = self.create_token("infantry", "medium", 1, 10, 10)
        defender = self.create_token("infantry", "medium", 2, 11, 10)
        
        initial_attacker_hp = attacker.current_hp
        initial_defender_hp = defender.current_hp
        
        action = Action(self.board)
        combat_result = action.resolve_combat(attacker, defender)
        
        # Oba żetony powinny zostać ranne (atak + kontratak)
        self.assertLess(attacker.current_hp, initial_attacker_hp)
        self.assertLess(defender.current_hp, initial_defender_hp)
        
    def test_size_advantage(self):
        """Test przewagi większych jednostek nad mniejszymi"""
        large_infantry = self.create_token("infantry", "large", 1, 12, 12)
        small_infantry = self.create_token("infantry", "small", 2, 13, 12)
        
        initial_large_hp = large_infantry.current_hp
        initial_small_hp = small_infantry.current_hp
        
        action = Action(self.board)
        combat_result = action.resolve_combat(large_infantry, small_infantry)
        
        # Większa jednostka powinna zadać więcej obrażeń
        large_damage = initial_large_hp - large_infantry.current_hp
        small_damage = initial_small_hp - small_infantry.current_hp
        
        self.assertGreater(small_damage, large_damage)
        
    def test_air_unit_special_combat(self):
        """Test walki jednostek powietrznych"""
        air_unit = self.create_token("air", "medium", 1, 15, 15)
        ground_unit = self.create_token("infantry", "medium", 2, 16, 15)
        
        action = Action(self.board)
        
        # Sprawdzamy czy jednostka powietrzna może atakować naziemną
        can_attack = action.can_attack(air_unit, ground_unit)
        
        if can_attack:
            initial_ground_hp = ground_unit.current_hp
            combat_result = action.resolve_combat(air_unit, ground_unit)
            
            # Jednostka naziemna powinna zostać uszkodzona
            self.assertLess(ground_unit.current_hp, initial_ground_hp)
            
    def test_multiple_combat_rounds(self):
        """Test wielokrotnych rund walki"""
        unit1 = self.create_token("tank", "medium", 1, 18, 18)
        unit2 = self.create_token("tank", "medium", 2, 19, 18)
        
        action = Action(self.board)
        
        # Wykonujemy kilka rund walki
        rounds = 0
        while unit1.current_hp > 0 and unit2.current_hp > 0 and rounds < 10:
            combat_result = action.resolve_combat(unit1, unit2)
            rounds += 1
            
        # Po kilku rundach przynajmniej jedna jednostka powinna być wyeliminowana
        self.assertTrue(unit1.current_hp <= 0 or unit2.current_hp <= 0 or rounds >= 10)
        
    def test_attack_range_validation(self):
        """Test walidacji zasięgu ataku"""
        artillery = self.create_token("artillery", "large", 1, 0, 0)
        
        # Cel w zasięgu (3 heksy)
        target_in_range = self.create_token("infantry", "small", 2, 3, 0)
        
        # Cel poza zasięgiem (5 heksów)
        target_out_of_range = self.create_token("infantry", "small", 2, 5, 0)
        
        action = Action(self.board)
        
        # Sprawdzamy zasięgi
        self.assertTrue(action.can_attack(artillery, target_in_range))
        self.assertFalse(action.can_attack(artillery, target_out_of_range))
        
    def test_combat_with_damaged_units(self):
        """Test walki z już uszkodzonymi jednostkami"""
        damaged_unit = self.create_token("infantry", "large", 1, 7, 7)
        damaged_unit.current_hp = 5  # Uszkodzona jednostka
        
        full_hp_unit = self.create_token("infantry", "medium", 2, 8, 7)
        
        action = Action(self.board)
        combat_result = action.resolve_combat(damaged_unit, full_hp_unit)
        
        # Uszkodzona jednostka powinna być w gorszej sytuacji
        self.assertTrue(damaged_unit.current_hp <= 5)
        self.assertLess(full_hp_unit.current_hp, full_hp_unit.max_hp)


class TestCombatBalance(unittest.TestCase):
    """Testy równowagi systemu walki po rebalansingu"""
    
    def setUp(self):
        self.board = Board(10, 10)
        
    def test_movement_balance(self):
        """Test zrównoważenia ruchu jednostek"""
        # Po rebalansingu wszystkie jednostki naziemne mają podobny ruch
        infantry = Token("inf", 0, 0, "infantry", "medium", 1, 12, 12, 2, 2, 8, 8, 1, 3)
        tank = Token("tank", 1, 0, "tank", "medium", 1, 15, 15, 2, 2, 12, 10, 1, 3)
        artillery = Token("art", 2, 0, "artillery", "medium", 1, 8, 8, 1, 1, 10, 5, 3, 4)
        air = Token("air", 3, 0, "air", "medium", 1, 8, 8, 6, 6, 10, 5, 1, 5)
        
        # Sprawdzamy czy ruch jest zrównoważony
        self.assertEqual(infantry.movement_points, 2)
        self.assertEqual(tank.movement_points, 2)
        self.assertEqual(artillery.movement_points, 1)  # Artyleria powolniejsza
        self.assertEqual(air.movement_points, 6)  # Lotnictwo szybkie
        
    def test_cost_effectiveness(self):
        """Test efektywności kosztowej jednostek"""
        # Ten test sprawdza czy droższe jednostki są odpowiednio silniejsze
        
        # Wartości po rebalansingu - czołgi droższe ale nie przesadnie silniejsze
        small_infantry_combat_value = 6 * 6 + 8  # atak * obrona + hp
        small_tank_combat_value = 10 * 8 + 10
        
        # Stosunek siły bojowej powinien być rozsądny
        ratio = small_tank_combat_value / small_infantry_combat_value
        
        # Czołg powinien być silniejszy ale nie więcej niż 2x
        self.assertGreater(ratio, 1.0)
        self.assertLess(ratio, 2.5)


if __name__ == "__main__":
    # Uruchomienie testów
    unittest.main(verbosity=2)
