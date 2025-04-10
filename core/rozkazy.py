"""
Moduł do obsługi rozkazów wydawanych jednostkom (np. ruch, atak).
Aktualnie zawiera podstawową strukturę, którą można rozszerzyć.
"""
class OrdersManager:
    """
    Klasa zarządzająca rozkazami dla jednostek.
    """
    def __init__(self):
        # Lista rozkazów (np. lista krotek (unit, order_type, target))
        self.orders = []

    def give_order(self, unit, order_type, target=None):
        """
        Dodaje rozkaz dla podanej jednostki.
        order_type może być np. "move", "attack" itp.
        """
        # Na razie dodajemy rozkaz do listy i wypisujemy informację (dla celów debugowania)
        self.orders.append((unit, order_type, target))
        print(f"[ROZKAZ] Jednostka {unit} otrzymała rozkaz: {order_type} {('na '+str(target)) if target else ''}")

    def clear_orders(self):
        """
        Usuwa wszystkie zaplanowane rozkazy.
        """
        self.orders.clear()
