import math

def get_hex_vertices(center_x, center_y, size):
    """
    Zwraca listę wierzchołków (x,y) dla heksa pointy-top,
    w układzie axial, z podanym rozmiarem (size).
    """
    verts = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        x = center_x + size * math.cos(angle)
        y = center_y + size * math.sin(angle)
        verts.append((x, y))
    return verts

def point_in_polygon(x, y, poly):
    """
    Ray-casting: sprawdza, czy punkt (x,y) jest wewnątrz wielokąta poly.
    poly to lista (x0,y0),(x1,y1),... wierzchołków.
    """
    inside = False
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        if ((y0 > y) != (y1 > y)) and (x < (x1 - x0) * (y - y0) / (y1 - y0) + x0):
            inside = not inside
    return inside