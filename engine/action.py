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
            return False, "Brak żetonu."
        player = None
        for p in getattr(engine, 'players', []):
            if hasattr(token, 'owner') and token.owner == f"{p.id} ({p.nation})":
                player = p
        start = (token.q, token.r)
        goal = (self.dest_q, self.dest_r)
        tile = engine.board.get_tile(self.dest_q, self.dest_r)
        if tile is None:
            return False, "Brak pola docelowego."
        # Usuwamy blokadę na wejście na pole z wrogiem, ale nie pozwalamy wejść na pole z sojusznikiem
        if engine.board.is_occupied(self.dest_q, self.dest_r):
            for t in engine.tokens:
                if t.q == self.dest_q and t.r == self.dest_r and t.owner == token.owner:
                    return False, "Pole zajęte przez sojusznika."
        max_mp = getattr(token, 'maxMovePoints', token.stats.get('move', 0))
        if not hasattr(token, 'currentMovePoints'):
            token.currentMovePoints = max_mp
        if not hasattr(token, 'maxMovePoints'):
            token.maxMovePoints = max_mp
        if not hasattr(token, 'maxFuel'):
            token.maxFuel = token.stats.get('maintenance', 0)
        if not hasattr(token, 'currentFuel'):
            token.currentFuel = token.maxFuel
        if token.currentMovePoints <= 0 or token.currentFuel <= 0:
            return False, "Brak punktów ruchu lub paliwa."
        if tile.move_mod == -1:
            return False, "Pole nieprzejezdne."
        # Jeśli pole docelowe jest zajęte przez wroga, znajdź najdalsze możliwe pole przed wrogiem
        path = engine.board.find_path(start, goal, max_cost=token.stats.get('move', 0))
        if not path:
            return False, "Brak ścieżki do celu."
        if not token.can_move_to(len(path)-1):
            return False, "Za daleko."
        path_cost = 0
        fuel_cost = 0
        final_pos = start
        # --- Poprawiona pętla: aktualizuj widoczność tylko do faktycznego zatrzymania ---
        for i, step in enumerate(path[1:]):  # pomijamy start
            # Każdy krok zużywa 1 paliwo
            if token.currentFuel <= 0:
                break
            final_pos = step
            path_cost += 1
            fuel_cost += 1
            token.currentFuel -= 1
            if token.currentMovePoints - path_cost < 0:
                break
        # Ustaw żeton na ostatniej osiągniętej pozycji
        token.set_position(*final_pos)
        token.currentMovePoints -= path_cost
        return True, "OK"

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
