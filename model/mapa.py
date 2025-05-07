import json, math
from model.hex_utils import get_hex_vertices, point_in_polygon

class Tile:
    def __init__(self, q, r, data):
        self.q = q
        self.r = r
        self.terrain_key   = data.get("terrain_key", "teren_płaski")
        self.move_mod      = data.get("move_mod", 0)
        self.defense_mod   = data.get("defense_mod", 0)
        self.type          = data.get("type", None)
        self.value         = data.get("value", None)
        self.spawn_nation  = None

class Mapa:
    def __init__(self, json_path):
        d = json.load(open(json_path, encoding="utf-8"))
        m = d["meta"]
        self.hex_size = m["hex_size"]
        self.cols     = m["cols"]
        self.rows     = m["rows"]
        # terrain
        self.terrain = {
            k: Tile(*map(int, k.split(",")), v)
            for k, v in d.get("terrain", {}).items()
        }
        # key_points
        for k, v in d.get("key_points", {}).items():
            t = self.terrain.get(k)
            if t:
                t.type  = v.get("type")
                t.value = v.get("value")
        # spawn_points
        for nation, coords in d.get("spawn_points", {}).items():
            for k in coords:
                t = self.terrain.get(k)
                if t:
                    t.spawn_nation = nation

    def _hex_center(self, q, r):
        s = self.hex_size
        x = s + q * 1.5 * s
        y = (math.sqrt(3)/2 * s) + r * math.sqrt(3) * s
        if q % 2 == 1:
            y += (math.sqrt(3) * s) / 2
        return x, y

    def coords_to_hex(self, x, y):
        for q in range(self.cols):
            for r in range(self.rows):
                cx, cy = self._hex_center(q, r)
                verts = get_hex_vertices(cx, cy, self.hex_size)
                if point_in_polygon(x, y, verts):
                    return q, r
        return None

    def get_tile(self, q, r):
        return self.terrain.get(f"{q},{r}")

    def get_overlay_items(self):
        """
        Zwraca listę:
            [(verts, (cx,cy), text), ...]
        text to:
            - 'spawn<nacja>' jeśli jest spawn
            - 'key<type><value>' jeśli jest key_point
            - 'm<move_mod>d<defense_mod>' w przeciwnym wypadku
        """
        items = []
        for key, tile in self.terrain.items():
            q, r = map(int, key.split(","))
            cx, cy = self._hex_center(q, r)
            verts = get_hex_vertices(cx, cy, self.hex_size)
            if tile.spawn_nation:
                txt = f"spawn{tile.spawn_nation.lower()}"
            elif tile.type and tile.value is not None:
                txt = f"key{tile.type}{tile.value}"
            else:
                txt = f"m{tile.move_mod}d{tile.defense_mod}"
            items.append((verts, (cx, cy), txt))
        return items