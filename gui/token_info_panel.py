import tkinter as tk

__all__ = ["TokenInfoPanel"]

class TokenInfoPanel(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.config(width=260, height=80)  # Stała wysokość
        self.pack_propagate(False)
        # Canvas + scrollbar
        self.canvas = tk.Canvas(self, width=260, height=80, highlightthickness=0)
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
        for i, key in enumerate(["nacja", "jednostka", "punkty_ruchu", "paliwo", "zasięg_widzenia", "wartość_bojowa"]):
            label = tk.Label(self.inner_frame, text=f"{key.capitalize()}: -", font=font, anchor="w")
            label.grid(row=i, column=0, sticky="w", padx=4, pady=2)
            self.labels[key] = label

    def show_token(self, token):
        if token is None:
            return
        nation = token.stats.get('nation', '-')
        unit_name = token.stats.get('label', token.id)
        current_mp = getattr(token, 'currentMovePoints', None)
        if current_mp is None:
            current_mp = token.stats.get('move', '-')
        sight = token.stats.get('sight', '-')
        current_fuel = getattr(token, 'currentFuel', token.stats.get('maintenance', '-'))
        max_fuel = getattr(token, 'maxFuel', token.stats.get('maintenance', '-'))
        combat_value = getattr(token, 'combat_value', token.stats.get('combat_value', '-'))
        self.labels["nacja"].config(text=f"Nacja: {nation}")
        self.labels["jednostka"].config(text=f"Jednostka: {unit_name}")
        self.labels["punkty_ruchu"].config(text=f"Punkty ruchu: {current_mp}")
        self.labels["paliwo"].config(text=f"Paliwo: {current_fuel}/{max_fuel}")
        self.labels["zasięg_widzenia"].config(text=f"Zasięg widzenia: {sight}")
        self.labels["wartość_bojowa"].config(text=f"Zasoby bojowe: {combat_value}")

    def clear(self):
        # Czyści wszystkie etykiety panelu do wartości domyślnych
        for key, label in self.labels.items():
            if key == "paliwo":
                label.config(text="Paliwo: -/-")
            else:
                label.config(text=f"{key.capitalize()}: -")
