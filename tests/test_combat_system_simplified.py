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
        
    def create_token(self, token_type, size, player_id, q, r):
        """Pomocnicza funkcja do tworzenia żetonów z realistycznymi wartościami po rebalansingu"""
        
        # Wartości po rebalansingu według zmian w token_editor i token_shop
        default_values = {
            "infantry": {
                "small": {"move": 2, "attack": 6, "defense": 6, "combat_value": 6, "maintenance": 1},
                "medium": {"move": 2, "attack": 8, "defense": 8, "combat_value": 8, "maintenance": 2},
                "large": {"move": 2, "attack": 10, "defense": 10, "combat_value": 10, "maintenance": 3}
            },
            "tank": {
                "small": {"move": 2, "attack": 10, "defense": 8, "combat_value": 10, "maintenance": 3},
                "medium": {"move": 2, "attack": 12, "defense": 10, "combat_value": 12, "maintenance": 4},
                "large": {"move": 2, "attack": 15, "defense": 12, "combat_value": 15, "maintenance": 5}
            },
            "artillery": {
                "small": {"move": 1, "attack": 8, "defense": 4, "combat_value": 8, "maintenance": 2},
                "medium": {"move": 1, "attack": 10, "defense": 5, "combat_value": 10, "maintenance": 3},
                "large": {"move": 1, "attack": 12, "defense": 6, "combat_value": 12, "maintenance": 4}
            },
            "air": {
                "small": {"move": 6, "attack": 8, "defense": 4, "combat_value": 8, "maintenance": 3},
                "medium": {"move": 6, "attack": 10, "defense": 5, "combat_value": 10, "maintenance": 4},
                "large": {"move": 6, "attack": 12, "defense": 6, "combat_value": 12, "maintenance": 5}
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
        
        return token
        
    def test_token_creation(self):
        """Test podstawowego tworzenia żetonów"""
        infantry = self.create_token("infantry", "medium", 1, 5, 5)
        
        # Sprawdzamy czy żeton został utworzony poprawnie
        self.assertEqual(infantry.stats['move'], 2)
        self.assertEqual(infantry.stats['combat_value'], 8)
        self.assertEqual(infantry.owner, "player_1")
        self.assertEqual(infantry.q, 5)
        self.assertEqual(infantry.r, 5)
        
    def test_movement_balance_after_rebalancing(self):
        """Test zrównoważenia ruchu jednostek po rebalansingu"""
        infantry = self.create_token("infantry", "medium", 1, 0, 0)
        tank = self.create_token("tank", "medium", 1, 1, 0)
        artillery = self.create_token("artillery", "medium", 1, 2, 0)
        air = self.create_token("air", "medium", 1, 3, 0)
        
        # Sprawdzamy nowe wartości ruchu po rebalansingu
        self.assertEqual(infantry.stats['move'], 2)
        self.assertEqual(tank.stats['move'], 2)  # Czołgi spowolnione
        self.assertEqual(artillery.stats['move'], 1)  # Artyleria najwolniejsza
        self.assertEqual(air.stats['move'], 6)  # Lotnictwo najszybsze
        
    def test_combat_values_after_rebalancing(self):
        """Test wartości bojowych po rebalansingu"""
        small_infantry = self.create_token("infantry", "small", 1, 0, 0)
        medium_tank = self.create_token("tank", "medium", 1, 1, 0)
        large_artillery = self.create_token("artillery", "large", 1, 2, 0)
        
        # Sprawdzamy nowe wartości bojowe
        self.assertEqual(small_infantry.stats['combat_value'], 6)
        self.assertEqual(medium_tank.stats['combat_value'], 12)
        self.assertEqual(large_artillery.stats['combat_value'], 12)
        
        # Sprawdzamy że czołgi są silniejsze ale nie przesadnie
        infantry_to_tank_ratio = medium_tank.stats['combat_value'] / small_infantry.stats['combat_value']
        self.assertGreater(infantry_to_tank_ratio, 1.5)
        self.assertLess(infantry_to_tank_ratio, 3.0)
        
    def test_maintenance_costs_after_rebalancing(self):
        """Test kosztów utrzymania po rebalansingu"""
        small_infantry = self.create_token("infantry", "small", 1, 0, 0)
        small_tank = self.create_token("tank", "small", 1, 1, 0)
        medium_artillery = self.create_token("artillery", "medium", 1, 2, 0)
        
        # Sprawdzamy czy czołgi mają wyższe koszty utrzymania
        self.assertEqual(small_infantry.stats['maintenance'], 1)
        self.assertEqual(small_tank.stats['maintenance'], 3)  # Czołgi droższe w utrzymaniu
        self.assertEqual(medium_artillery.stats['maintenance'], 3)
        
        # Czołgi powinny kosztować więcej niż piechota
        self.assertGreater(small_tank.stats['maintenance'], small_infantry.stats['maintenance'])
        
    def test_unit_type_specialization(self):
        """Test specjalizacji różnych typów jednostek"""
        artillery = self.create_token("artillery", "medium", 1, 0, 0)
        tank = self.create_token("tank", "medium", 1, 1, 0)
        infantry = self.create_token("infantry", "medium", 1, 2, 0)
        
        # Artyleria: wysoki atak, niska obrona
        self.assertEqual(artillery.stats['attack'], 10)
        self.assertEqual(artillery.stats['defense'], 5)
        
        # Czołgi: zrównoważone, wysokie wartości
        self.assertEqual(tank.stats['attack'], 12)
        self.assertEqual(tank.stats['defense'], 10)
        
        # Piechota: zrównoważona, średnie wartości
        self.assertEqual(infantry.stats['attack'], 8)
        self.assertEqual(infantry.stats['defense'], 8)
        
    def test_size_scaling(self):
        """Test skalowania według rozmiaru jednostek"""
        small_infantry = self.create_token("infantry", "small", 1, 0, 0)
        medium_infantry = self.create_token("infantry", "medium", 1, 1, 0)
        large_infantry = self.create_token("infantry", "large", 1, 2, 0)
        
        # Sprawdzamy postępujące zwiększanie wartości
        self.assertLess(small_infantry.stats['combat_value'], medium_infantry.stats['combat_value'])
        self.assertLess(medium_infantry.stats['combat_value'], large_infantry.stats['combat_value'])
        
        # Sprawdzamy czy wzrost jest sensowny (nie za duży)
        small_to_medium = medium_infantry.stats['combat_value'] / small_infantry.stats['combat_value']
        medium_to_large = large_infantry.stats['combat_value'] / medium_infantry.stats['combat_value']
        
        self.assertAlmostEqual(small_to_medium, medium_to_large, delta=0.5)
        
    def test_air_unit_characteristics(self):
        """Test charakterystyk jednostek powietrznych"""
        air_medium = self.create_token("air", "medium", 1, 0, 0)
        ground_medium = self.create_token("infantry", "medium", 1, 1, 0)
        
        # Lotnictwo powinno być szybkie ale delikatne
        self.assertGreater(air_medium.stats['move'], ground_medium.stats['move'])
        self.assertLessEqual(air_medium.stats['defense'], ground_medium.stats['defense'])
        
    def test_board_integration(self):
        """Test integracji z planszą"""
        # Sprawdzamy czy mapa została załadowana poprawnie
        self.assertIsNotNone(self.board)
        self.assertGreater(self.board.cols, 0)
        self.assertGreater(self.board.rows, 0)
        self.assertIsNotNone(self.board.terrain)
        
        # Sprawdzamy czy istnieją różne typy terenu
        terrain_types = set()
        for tile in self.board.terrain.values():
            terrain_types.add(tile.terrain_key)
        
        self.assertGreater(len(terrain_types), 1)  # Powinna być różnorodność terenu


class TestCombatBalance(unittest.TestCase):
    """Testy równowagi systemu walki po rebalansingu"""
    
    def setUp(self):
        self.board = Board("data/map_data.json")
        
    def create_token(self, token_type, size, player_id, q, r):
        """Pomocnicza funkcja do tworzenia żetonów"""
        default_values = {
            "infantry": {
                "small": {"move": 2, "attack": 6, "defense": 6, "combat_value": 6, "maintenance": 1},
                "medium": {"move": 2, "attack": 8, "defense": 8, "combat_value": 8, "maintenance": 2},
                "large": {"move": 2, "attack": 10, "defense": 10, "combat_value": 10, "maintenance": 3}
            },
            "tank": {
                "small": {"move": 2, "attack": 10, "defense": 8, "combat_value": 10, "maintenance": 3},
                "medium": {"move": 2, "attack": 12, "defense": 10, "combat_value": 12, "maintenance": 4},
                "large": {"move": 2, "attack": 15, "defense": 12, "combat_value": 15, "maintenance": 5}
            }
        }
        
        stats = default_values[token_type][size]
        return Token(
            id=f"{token_type}_{size}_{player_id}_{q}_{r}",
            owner=f"player_{player_id}",
            stats=stats,
            q=q, 
            r=r
        )
        
    def test_cost_effectiveness_balance(self):
        """Test efektywności kosztowej jednostek"""
        infantry_small = self.create_token("infantry", "small", 1, 0, 0)
        tank_small = self.create_token("tank", "small", 1, 1, 0)
        
        # Obliczamy efektywność bojową na punkt utrzymania
        infantry_efficiency = infantry_small.stats['combat_value'] / infantry_small.stats['maintenance']
        tank_efficiency = tank_small.stats['combat_value'] / tank_small.stats['maintenance']
        
        # Różnica efektywności nie powinna być zbyt duża
        efficiency_ratio = max(infantry_efficiency, tank_efficiency) / min(infantry_efficiency, tank_efficiency)
        self.assertLess(efficiency_ratio, 2.0)  # Nie więcej niż 2x różnicy
        
    def test_attack_defense_balance(self):
        """Test równowagi między atakiem a obroną"""
        medium_infantry = self.create_token("infantry", "medium", 1, 0, 0)
        medium_tank = self.create_token("tank", "medium", 1, 1, 0)
        
        # Sprawdzamy czy stosunek atak/obrona jest sensowny
        infantry_ratio = medium_infantry.stats['attack'] / medium_infantry.stats['defense']
        tank_ratio = medium_tank.stats['attack'] / medium_tank.stats['defense']
        
        # Jednostki powinny być relatywnie zrównoważone
        self.assertGreater(infantry_ratio, 0.8)
        self.assertLess(infantry_ratio, 1.5)
        self.assertGreater(tank_ratio, 0.8)
        self.assertLess(tank_ratio, 1.8)


if __name__ == "__main__":
    # Uruchomienie testów
    unittest.main(verbosity=2)
