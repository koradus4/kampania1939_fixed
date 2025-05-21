import math

def get_hex_vertices(cx, cy, s):
    angles = [math.radians(60 * i) for i in range(6)]
    return [(cx + s * math.cos(a), cy + s * math.sin(a)) for a in angles]

def point_in_polygon(x, y, poly):
    inside = False
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        if ((y0 > y) != (y1 > y)) and (x < (x1 - x0) * (y - y0) / (y1 - y0) + x0):
            inside = not inside
    return inside
