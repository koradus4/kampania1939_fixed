import tkinter as tk

__all__ = ["TokenInfoPanel"]

class TokenInfoPanel(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.config(width=260, height=90)  # ZMNIEJSZONA wysokość
        self.pack_propagate(False)
        self.labels = {}
        self._build()

    def _build(self):
        font = ("Arial", 11)
        for i, key in enumerate(["nacja", "jednostka", "punkty_ruchu"]):
            label = tk.Label(self, text=f"{key.capitalize()}: -", font=font, anchor="w")
            label.grid(row=i, column=0, sticky="w", padx=4, pady=2)
            self.labels[key] = label

    def show_token(self, token):
        nation = token.stats.get('nation', '-')
        unit_name = token.stats.get('label', token.id)
        current_mp = getattr(token, 'currentMovePoints', None)
        if current_mp is None:
            current_mp = token.stats.get('move', '-')
        self.labels["nacja"].config(text=f"Nacja: {nation}")
        self.labels["jednostka"].config(text=f"Jednostka: {unit_name}")
        self.labels["punkty_ruchu"].config(text=f"Punkty ruchu: {current_mp}")

    def clear(self):
        for key, label in self.labels.items():
            label.config(text=f"{key.capitalize()}: -")
