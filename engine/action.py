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
        player = None
        for p in getattr(engine, 'players', []):
            if hasattr(token, 'owner') and token.owner == f"{p.id} ({p.nation})":
                player = p
                break
        start = (token.q, token.r)
        goal = (self.dest_q, self.dest_r)
        tile = engine.board.get_tile(self.dest_q, self.dest_r)
        if tile is None:
            return False, "Pole docelowe nie istnieje na mapie."
        # Usuwamy blokadę na wejście na pole z wrogiem, ale nie pozwalamy wejść na pole z sojusznikiem
        if engine.board.is_occupied(self.dest_q, self.dest_r):
            for t in engine.tokens:
                if t.q == self.dest_q and t.r == self.dest_r and t.id != token.id:
                    if t.owner == token.owner:
                        return False, "Pole zajęte przez sojuszniczy żeton."
        max_mp = getattr(token, 'maxMovePoints', token.stats.get('move', 0))
        if not hasattr(token, 'currentMovePoints'):
            token.currentMovePoints = max_mp
        if not hasattr(token, 'maxMovePoints'):
            token.maxMovePoints = max_mp
        if token.currentMovePoints <= 0:
            return False, "Brak punktów ruchu."
        if tile.move_mod == -1:
            return False, "Pole nieprzekraczalne (move_mod == -1)."
        path = engine.board.find_path(start, goal, max_cost=token.stats.get('move', 0))
        if not path:
            return False, "Brak możliwej ścieżki."
        if not token.can_move_to(len(path)-1):
            return False, "Za daleko."
        path_cost = 0
        final_pos = start
        for i, step in enumerate(path[1:]):  # pomijamy start
            tile = engine.board.get_tile(*step)
            if not tile:
                return False, "Błąd mapy: brak pola na trasie."
            temp_q, temp_r = step
            vision_range = token.stats.get('sight', 0)
            visible_hexes = set()
            for dq in range(-vision_range, vision_range + 1):
                for dr in range(-vision_range, vision_range + 1):
                    q = temp_q + dq
                    r = temp_r + dr
                    if engine.board.hex_distance((temp_q, temp_r), (q, r)) <= vision_range:
                        if engine.board.get_tile(q, r) is not None:
                            visible_hexes.add((q, r))
            if player is not None:
                player.temp_visible_hexes |= visible_hexes
            # Czy na tym polu jest wróg? Jeśli tak, zatrzymaj ruch na poprzednim polu
            enemy_on_tile = False
            for t in engine.tokens:
                if t.q == step[0] and t.r == step[1] and t.id != token.id and t.owner != token.owner:
                    enemy_on_tile = True
            if enemy_on_tile:
                # Zatrzymaj ruch na poprzednim polu
                break
            # Czy w zasięgu widzenia jest wróg? Jeśli tak, zatrzymaj ruch na tym polu
            for t in engine.tokens:
                if t.id != token.id and t.owner != token.owner and (t.q, t.r) in visible_hexes:
                    final_pos = step
                    path_cost += 1 + tile.move_mod
                    token.set_position(*final_pos)
                    token.currentMovePoints -= path_cost
                    return True, f"Ruch zatrzymany: wykryto wroga w zasięgu widzenia na polu {final_pos} (koszt: {path_cost}, pozostało MP: {token.currentMovePoints})"
            # Blokada na sojusznika na polu docelowym
            for t in engine.tokens:
                if t.q == step[0] and t.r == step[1] and t.id != token.id:
                    if t.owner == token.owner:
                        return False, "Pole zajęte przez sojuszniczy żeton."
            path_cost += 1 + tile.move_mod
            final_pos = step
        if token.currentMovePoints < path_cost:
            return False, f"Za mało punktów ruchu (koszt: {path_cost}, dostępne: {token.currentMovePoints})"
        token.set_position(*final_pos)
        token.currentMovePoints -= path_cost
        return True, f"Ruch wykonany na {final_pos} (koszt: {path_cost}, pozostało MP: {token.currentMovePoints})"

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
