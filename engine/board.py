import json
from typing import Dict, Tuple, Optional, List
from engine.hex_utils import get_hex_vertices, point_in_polygon

class Tile:
    def __init__(self, q: int, r: int, data: Dict):
        self.q = q
        self.r = r
        self.terrain_key = data.get("terrain_key", "teren_płaski")
        self.move_mod = data.get("move_mod", 0)
        self.defense_mod = data.get("defense_mod", 0)
        self.type = data.get("type", None)
        self.value = data.get("value", None)
        self.spawn_nation = data.get("spawn_nation", None)

class Board:
    def __init__(self, json_path: str):
        with open(json_path, encoding="utf-8") as f:
            d = json.load(f)
        m = d["meta"]
        self.hex_size = m["hex_size"]
        self.cols = m["cols"]
        self.rows = m["rows"]
        # terrain
        self.terrain = {
            k: Tile(*map(int, k.split(",")), v)
            for k, v in d.get("terrain", {}).items()
        }
        # Dodano: spawn_points
        self.spawn_points = d.get("spawn_points", {})
        # Ustaw spawn_nation w terrain na podstawie spawn_points
        for nation, hex_list in self.spawn_points.items():
            for hex_id in hex_list:
                tile = self.terrain.get(hex_id)
                if tile:
                    tile.spawn_nation = nation
        # key_points można dodać później

    def hex_to_pixel(self, q: int, r: int) -> Tuple[float, float]:
        # Axial -> pixel (dla pointy-top) z offsetem, by heks 0,0 był w pełni widoczny
        s = self.hex_size
        dx = s  # przesunięcie w prawo o promień heksa
        dy = s * (3**0.5) / 2  # przesunięcie w dół o połowę wysokości heksa
        x = s * (3/2 * q) + dx
        y = s * (3**0.5 * (r + q/2)) + dy
        return (x, y)

    def pixel_to_hex(self, x: float, y: float) -> Tuple[int, int]:
        # Szybkie przeliczanie pixel -> axial (dla pointy-top)
        s = self.hex_size
        q = (2/3 * x) / s
        r = ((-1/3 * x) + (3**0.5/3 * y)) / s
        return self._hex_round(q, r)

    def _hex_round(self, qf: float, rf: float) -> Tuple[int, int]:
        # Zaokrąglanie współrzędnych cube -> axial
        sf = -qf - rf
        q = round(qf)
        r = round(rf)
        s = round(sf)
        dq = abs(q - qf)
        dr = abs(r - rf)
        ds = abs(s - sf)
        if dq > dr and dq > ds:
            q = -r - s
        elif dr > ds:
            r = -q - s
        # s = -q - r
        return (q, r)

    def get_tile(self, q: int, r: int) -> Optional[Tile]:
        return self.terrain.get(f"{q},{r}")

    def set_tokens(self, tokens: List):
        """Przypisz listę żetonów do planszy (do obsługi kolizji, pathfindingu itp.).
        UWAGA: Jeśli zmieniasz pozycje żetonów ręcznie (np. w testach), wywołaj ponownie set_tokens po zmianie!"""
        self.tokens = tokens

    def is_occupied(self, q: int, r: int, visible_tokens: Optional[set] = None) -> bool:
        """Sprawdza, czy pole jest zajęte przez żeton. Jeśli podano visible_tokens, sprawdza tylko żetony widoczne."""
        if visible_tokens is not None:
            return any(t.q == q and t.r == r and t.id in visible_tokens for t in getattr(self, 'tokens', []))
        return any(t.q == q and t.r == r for t in getattr(self, 'tokens', []))

    def neighbors(self, q: int, r: int) -> List[Tuple[int, int]]:
        """Zwraca listę sąsiadów heksa (axial)."""
        directions = [(+1, 0), (+1, -1), (0, -1), (-1, 0), (-1, +1), (0, +1)]
        return [(q+dq, r+dr) for dq, dr in directions]

    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int], max_mp: int = 99, max_fuel: int = 99, visible_tokens: Optional[set] = None) -> Optional[List[Tuple[int, int]]]:
        """Prosty pathfinding A* (uwzględnia move_mod, zajętość pól, MP i paliwo, widoczność wrogów)."""
        import heapq
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        cost_so_far = {start: (0, 0)}  # (mp_cost, fuel_cost)
        while open_set:
            _, current = heapq.heappop(open_set)
            if current == goal:
                # Odtwórz ścieżkę
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                return path[::-1]
            for neighbor in self.neighbors(*current):
                tile = self.get_tile(*neighbor)
                print(f"[DEBUG][PATH] Rozważam neighbor={neighbor}, tile={tile}, move_mod={getattr(tile, 'move_mod', None) if tile else None}")
                if not tile:
                    print(f"[DEBUG][PATH] Odrzucam {neighbor} - brak tile")
                    continue
                if self.is_occupied(*neighbor, visible_tokens=visible_tokens):
                    print(f"[DEBUG][PATH] Odrzucam {neighbor} - zajęte")
                    continue
                if tile.move_mod == -1:
                    print(f"[DEBUG][PATH] Odrzucam {neighbor} - nieprzejezdne")
                    continue
                move_cost = 1 + tile.move_mod
                new_mp = cost_so_far[current][0] + move_cost
                new_fuel = cost_so_far[current][1] + move_cost
                if new_mp > max_mp or new_fuel > max_fuel:
                    print(f"[DEBUG][PATH] Odrzucam {neighbor} - za drogo (mp={new_mp}, fuel={new_fuel})")
                    continue
                if neighbor not in cost_so_far or (new_mp, new_fuel) < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = (new_mp, new_fuel)
                    priority = new_mp + self.hex_distance(neighbor, goal)
                    heapq.heappush(open_set, (priority, neighbor))
                    came_from[neighbor] = current
        return None

    def hex_distance(self, a: Tuple[int, int], b: Tuple[int, int]) -> int:
        """Dystans heksowy (axial)."""
        aq, ar = a
        bq, br = b
        return int((abs(aq - bq) + abs(aq + ar - bq - br) + abs(ar - br)) / 2)

    def coords_to_hex(self, x, y):
        # Nowa wersja: iteruj po wszystkich kluczach terrain (q,r mogą być ujemne)
        for hex_id in self.terrain:
            q, r = map(int, hex_id.split(","))
            cx, cy = self.hex_to_pixel(q, r)
            verts = get_hex_vertices(cx, cy, self.hex_size)
            if point_in_polygon(x, y, verts):
                return q, r
        return None

    def get_overlay_items(self):
        items = []
        for key, tile in self.terrain.items():
            q, r = map(int, key.split(","))
            cx, cy = self.hex_to_pixel(q, r)
            verts = get_hex_vertices(cx, cy, self.hex_size)
            if tile.spawn_nation:
                txt = f"spawn{tile.spawn_nation.lower()}"
            elif tile.type and tile.value is not None:
                txt = f"key{tile.type}{tile.value}"
            else:
                txt = f"m{tile.move_mod}d{tile.defense_mod}"
            items.append((verts, (cx, cy), txt))
        return items
    # Pathfinding (A*) i inne metody będą dodane w kolejnych krokach
