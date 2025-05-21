class Action:
    def __init__(self, token_id):
        self.token_id = token_id

    def execute(self, engine):
        raise NotImplementedError("Każda akcja musi implementować execute!")

class MoveAction(Action):
    def __init__(self, token_id, dest_q, dest_r):
        super().__init__(token_id)
        self.dest_q = dest_q
        self.dest_r = dest_r

    def execute(self, engine):
        # Znajdź żeton
        token = next((t for t in engine.tokens if t.id == self.token_id), None)
        if not token:
            return False, "Nie znaleziono żetonu."
        start = (token.q, token.r)
        goal = (self.dest_q, self.dest_r)
        # WALIDACJA przed zmianą pozycji!
        path = engine.board.find_path(start, goal, max_cost=token.stats.get('move', 0))
        if not path:
            return False, "Brak możliwej ścieżki."
        if not token.can_move_to(len(path)-1):
            return False, "Za daleko."
        if engine.board.is_occupied(self.dest_q, self.dest_r):
            return False, "Pole zajęte."
        # Wykonaj ruch dopiero po walidacji
        token.set_position(self.dest_q, self.dest_r)
        return True, f"Ruch wykonany na {self.dest_q},{self.dest_r}"

class CombatAction(Action):
    def __init__(self, attacker_id, defender_id):
        super().__init__(attacker_id)
        self.defender_id = defender_id

    def execute(self, engine):
        # Prosty szkic: walka dwóch żetonów
        attacker = next((t for t in engine.tokens if t.id == self.token_id), None)
        defender = next((t for t in engine.tokens if t.id == self.defender_id), None)
        if not attacker or not defender:
            return False, "Brak żetonu atakującego lub broniącego."
        # Sprawdź dystans
        dist = engine.board.hex_distance((attacker.q, attacker.r), (defender.q, defender.r))
        if dist > 1:
            return False, "Za daleko do ataku."
        # Prosta mechanika walki
        if attacker.stats.get('combat_value', 0) > defender.stats.get('combat_value', 0):
            # Usuwamy obrońcę
            engine.tokens.remove(defender)
            return True, "Obrońca zniszczony."
        else:
            return True, "Atak nieudany."
