import tkinter as tk

__all__ = ["TokenInfoPanel"]

class TokenInfoPanel(tk.Frame):
    def __init__(self, parent, **kwargs):
        height = kwargs.pop('height', 120)
        super().__init__(parent, **kwargs)
        self.config(width=260, height=height)  # Stała wysokość
        self.pack_propagate(False)
        # Canvas + scrollbar
        self.canvas = tk.Canvas(self, width=260, height=height, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner_frame = tk.Frame(self.canvas)
        self.inner_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.labels = {}
        self._build()

    def _build(self):
        font = ("Arial", 11)
        keys = [
            "nacja", "jednostka", "punkty_ruchu", "wartość_obrony", "tryb_ruchu",
            "paliwo", "zasięg_widzenia", "wartość_bojowa", "zasięg_ataku", "siła_ataku"
        ]
        for i, key in enumerate(keys):
            label = tk.Label(self.inner_frame, text=f"{key.capitalize()}: -", font=font, anchor="w")
            label.grid(row=i, column=0, sticky="w", padx=4, pady=1)
            self.labels[key] = label

    def show_token(self, token):
        if token is None:
            for key in self.labels:
                self.labels[key].config(text=f"{key.capitalize()}: -")
            return
        nation = token.stats.get('nation', '-')
        # Dodaj informację o właścicielu/dowódcy w formacie 'Dowódca X'
        owner_info = ''
        # Próbuj wyciągnąć numer dowódcy z owner lub commander_id
        dowodca_id = None
        if hasattr(token, 'commander_id') and token.commander_id:
            dowodca_id = token.commander_id
        elif hasattr(token, 'owner') and token.owner:
            # Spróbuj wyciągnąć numer z owner, np. '5 (Niemcy)' lub '2 (Polska)'
            import re
            m = re.match(r"(\d+)", str(token.owner))
            if m:
                dowodca_id = m.group(1)
        if dowodca_id:
            owner_info = f" / Dowódca {dowodca_id}"
        nation_label = f"Nacja: {nation}{owner_info}"
        unit_name = token.stats.get('unit_full_name') or token.stats.get('label', token.id)
        move = getattr(token, 'currentMovePoints', token.stats.get('move', '-'))
        base_move = getattr(token, 'base_move', token.stats.get('move', '-'))
        defense = getattr(token, 'defense_value', token.stats.get('defense_value', '-'))
        base_defense = getattr(token, 'base_defense', token.stats.get('defense_value', '-'))
        sight = token.stats.get('sight', '-')
        current_fuel = getattr(token, 'currentFuel', token.stats.get('maintenance', '-'))
        max_fuel = getattr(token, 'maxFuel', token.stats.get('maintenance', '-'))
        combat_value = getattr(token, 'combat_value', token.stats.get('combat_value', '-'))
        base_combat_value = token.stats.get('combat_value', '-')
        movement_mode = getattr(token, 'movement_mode', 'combat')
        mode_label = {'combat': 'Bojowy', 'march': 'Marsz', 'recon': 'Zwiad'}.get(movement_mode, movement_mode)
        attack = token.stats.get('attack', '-')
        if isinstance(attack, dict):
            attack_range = attack.get('range', '-')
            attack_value = attack.get('value', '-')
        elif isinstance(attack, int):
            attack_range = '-'
            attack_value = attack
        else:
            attack_range = '-'
            attack_value = '-'
        self.labels["nacja"].config(text=nation_label)
        self.labels["jednostka"].config(text=f"Jednostka: {unit_name}")
        self.labels["punkty_ruchu"].config(text=f"Punkty ruchu: {move} (bazowo: {base_move})")
        self.labels["wartość_obrony"].config(text=f"Wartość obrony: {defense} (bazowo: {base_defense})")
        self.labels["tryb_ruchu"].config(text=f"Tryb ruchu: {mode_label}")
        self.labels["paliwo"].config(text=f"Paliwo: {current_fuel}/{max_fuel}")
        self.labels["zasięg_widzenia"].config(text=f"Zasięg widzenia: {sight}")
        self.labels["wartość_bojowa"].config(text=f"Zasoby bojowe: {combat_value} (bazowo: {base_combat_value})")
        self.labels["zasięg_ataku"].config(text=f"Zasięg ataku: {attack_range}")
        self.labels["siła_ataku"].config(text=f"Siła ataku: {attack_value}")

    def clear(self):
        # Czyści wszystkie etykiety panelu do wartości domyślnych
        for key, label in self.labels.items():
            if key == "paliwo":
                label.config(text="Paliwo: -/-")
            else:
                label.config(text=f"{key.capitalize()}: -")
