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
        # --- MNOŻNIKI TRYBÓW RUCHU ---
        movement_mode = getattr(token, 'movement_mode', 'combat')
        token.apply_movement_mode()  # Ustaw aktualne wartości ruchu i obrony
        max_mp = token.currentMovePoints
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
        # Pathfinding
        # Ustal widoczne żetony dla gracza (jeśli gracz istnieje)
        visible_tokens = None
        if player is not None and hasattr(player, 'visible_tokens'):
            visible_tokens = set(player.visible_tokens)
        path = engine.board.find_path(start, goal, max_mp=token.currentMovePoints, max_fuel=token.currentFuel, visible_tokens=visible_tokens)
        if not path:
            return False, "Brak ścieżki do celu."
        # Oblicz koszt ruchu i paliwa po ścieżce
        path_cost = 0
        fuel_cost = 0
        final_pos = start
        board = engine.board
        sight = token.stats.get('sight', 0)
        for i, step in enumerate(path[1:]):  # pomijamy start
            tile = board.get_tile(*step)
            move_mod = getattr(tile, 'move_mod', 0)
            move_cost = 1 + move_mod  # zawsze minimum 1, np. bagno 1+3=4, las 1+2=3, płaski 1+0=1
            if token.currentMovePoints - (path_cost + move_cost) < 0 or token.currentFuel - (fuel_cost + move_cost) < 0:
                break  # nie stać na kolejny krok
            # Wyznacz pole widzenia z tego heksu
            visible_hexes = set()
            for dq in range(-sight, sight + 1):
                for dr in range(-sight, sight + 1):
                    q = step[0] + dq
                    r = step[1] + dr
                    if board.hex_distance(step, (q, r)) <= sight:
                        if board.get_tile(q, r) is not None:
                            visible_hexes.add((q, r))
            # Sprawdź, czy w polu widzenia jest przeciwnik (ignoruj sojuszników)
            enemy_in_sight = False
            for t in engine.tokens:
                # Pomijaj żetony bez ownera lub o pustym ownerze
                if not hasattr(t, 'owner') or not hasattr(token, 'owner') or not t.owner or not token.owner:
                    continue
                if (t.q, t.r) in visible_hexes:
                    nation1 = t.owner.split('(')[-1].replace(')','').strip()
                    nation2 = token.owner.split('(')[-1].replace(')','').strip()
                    if nation1 != nation2:
                        enemy_in_sight = True
                        break  # zatrzymaj ruch tylko na przeciwniku
            # --- PRINTY DEBUGUJĄCE ---
            print(f"[RUCH] Żeton {token.id} ({getattr(token, 'name', '')})")
            print(f"  Tryb ruchu: {getattr(token, 'movement_mode', 'combat')}")
            print(f"  Przed ruchem: MP={token.currentMovePoints-path_cost}, Paliwo={token.currentFuel-fuel_cost}")
            print(f"  Wchodzi na heks: {step}, move_mod={move_mod}")
            print(f"  Koszt wejścia: {move_cost} MP, {move_cost} paliwo")
            # --- KONIEC PRINTÓW ---
            final_pos = step
            path_cost += move_cost
            fuel_cost += move_cost
            if enemy_in_sight:
                print("  Przeciwnik w polu widzenia – ruch zatrzymany.")
                break  # Zatrzymaj ruch natychmiast
        if final_pos == start:
            return False, "Brak wystarczających punktów ruchu lub paliwa na ruch."
        # Ustaw żeton na ostatniej osiągniętej pozycji
        token.set_position(*final_pos)
        token.currentMovePoints -= path_cost
        token.currentFuel -= fuel_cost

        # --- ODKRYWANIE CAŁEGO POLA WIDZENIA NA TRASIE RUCHU ---
        if player is not None:
            for hex_coords in path[:path.index(final_pos)+1]:
                # Wyznacz pole widzenia z tego heksu
                visible_hexes = set()
                for dq in range(-sight, sight + 1):
                    for dr in range(-sight, sight + 1):
                        q = hex_coords[0] + dq
                        r = hex_coords[1] + dr
                        if board.hex_distance(hex_coords, (q, r)) <= sight:
                            if board.get_tile(q, r) is not None:
                                visible_hexes.add((q, r))
                player.temp_visible_hexes.update(visible_hexes)
                # Dodaj żetony przeciwnika z tych heksów
                for vh in visible_hexes:
                    for t in getattr(engine, 'tokens', []):
                        if (t.q, t.r) == vh and hasattr(t, 'owner') and hasattr(token, 'owner'):
                            nation1 = t.owner.split('(')[-1].replace(')','').strip()
                            nation2 = token.owner.split('(')[-1].replace(')','').strip()
                            if nation1 != nation2:
                                player.temp_visible_tokens.add(t.id)

        return True, "OK"

class CombatAction(Action):
    def __init__(self, attacker_id, defender_id):
        super().__init__(attacker_id)
        self.defender_id = defender_id

    def execute(self, engine):
        import random
        attacker = next((t for t in engine.tokens if t.id == self.token_id), None)
        defender = next((t for t in engine.tokens if t.id == self.defender_id), None)
        if not attacker or not defender:
            return False, "Brak żetonu atakującego lub broniącego."
        # Sprawdź dystans (zasięg ataku)
        attack_range = attacker.stats.get('attack', {}).get('range', 1)
        defense_range = defender.stats.get('attack', {}).get('range', 1)
        dist = engine.board.hex_distance((attacker.q, attacker.r), (defender.q, defender.r))
        if dist > attack_range:
            return False, f"Za daleko do ataku (zasięg: {attack_range})."
        # Sprawdź punkty ruchu
        if getattr(attacker, 'currentMovePoints', 0) <= 0:
            print("[DEBUG] Brak punktów ruchu do ataku.")
            return False, "Brak punktów ruchu do ataku."
        # Atak kosztuje wszystkie pozostałe MP (atak tylko raz na turę)
        attacker.currentMovePoints = 0
        # --- Rozstrzyganie walki ---
        # Atakujący
        attack_val = attacker.stats.get('attack', {}).get('value', 0)
        attack_mult = random.uniform(0.8, 1.2)
        attack_result = int(round(attack_val * attack_mult))
        # Obrońca
        defense_val = defender.stats.get('defense_value', 0)
        tile = engine.board.get_tile(defender.q, defender.r)
        defense_mod = tile.defense_mod if tile else 0
        defense_total = defense_val + defense_mod
        defense_mult = random.uniform(0.8, 1.2)
        # --- PRINTY DEBUGUJĄCE WALKĘ ---
        print(f"[WALKA] Atakujący: {attacker.id} ({getattr(attacker, 'name', '')}) na {attacker.q},{attacker.r}")
        print(f"  Obrońca: {defender.id} ({getattr(defender, 'name', '')}) na {defender.q},{defender.r}")
        print(f"  Zasięg ataku: {attack_range}, dystans: {dist}")
        print(f"  Zasięg ataku obrońcy: {defense_range}")
        # Atak jednostronny jeśli obrońca nie sięga atakującego
        if dist > defense_range:
            print("  Obrońca nie może kontratakować (za mały zasięg) – atak jednostronny.")
            defense_result = 0  # brak kontrataku
        else:
            print("  Obrońca kontratakuje!")
            defense_result = int(round(defense_total * defense_mult))
        print(f"  Atak: {attack_val} x {attack_mult:.2f} = {attack_result}")
        print(f"  Obrona: {defense_val} + modyfikator terenu {defense_mod} = {defense_total} x {defense_mult:.2f} = {defense_result}")
        print(f"  Straty: obrońca -{attack_result}, atakujący -{defense_result}")
        # Odejmij straty
        defender.combat_value = max(0, getattr(defender, 'combat_value', 0) - attack_result)
        attacker.combat_value = max(0, getattr(attacker, 'combat_value', 0) - defense_result)
        # NIE NADPISUJEMY stats['combat_value']!
        # defender.stats['combat_value'] = defender.combat_value  # USUNIĘTO! To jest wartość bazowa, nie zmieniamy jej.
        # attacker.stats['combat_value'] = attacker.combat_value  # USUNIĘTO!
        print(f"  Po walce: obrońca {defender.combat_value}, atakujący {attacker.combat_value}")
        # Eliminacja obrońcy
        if defender.combat_value <= 0:
            if random.random() < 0.5:
                defender.combat_value = 1
                # defender.stats['combat_value'] = 1  # USUNIĘTO!
                # Cofnij obrońcę o 1 pole (prosty algorytm: odsuń od atakującego)
                dq = defender.q - attacker.q
                dr = defender.r - attacker.r
                new_q = defender.q + (1 if dq > 0 else -1 if dq < 0 else 0)
                new_r = defender.r + (1 if dr > 0 else -1 if dr < 0 else 0)
                # Sprawdź czy pole jest wolne
                if not engine.board.is_occupied(new_q, new_r) and engine.board.get_tile(new_q, new_r):
                    defender.set_position(new_q, new_r)
                    msg = f"Obrońca przeżył z 1 punktem i cofnął się na ({new_q},{new_r})!"
                else:
                    # Jeśli nie można się cofnąć, żeton ginie
                    engine.tokens.remove(defender)
                    msg = "Obrońca nie mógł się cofnąć i został zniszczony!"
            else:
                engine.tokens.remove(defender)
                msg = "Obrońca został zniszczony!"
        else:
            msg = f"Obrońca stracił {attack_result} punktów, pozostało: {defender.combat_value}"
        # Eliminacja atakującego
        if attacker.combat_value <= 0:
            engine.tokens.remove(attacker)
            msg += "\nAtakujący został zniszczony!"
        else:
            msg += f"\nAtakujący stracił {defense_result} punktów, pozostało: {attacker.combat_value}"
        # --- KONIEC PRINTÓW ---
        return True, msg
