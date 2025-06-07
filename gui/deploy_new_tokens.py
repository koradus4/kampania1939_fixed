import tkinter as tk
from tkinter import messagebox
from pathlib import Path

class DeployNewTokensWindow(tk.Toplevel):
    def __init__(self, parent, gracz):
        super().__init__(parent)
        self.gracz = gracz
        self.title(f"Wystawianie nowych jednostek – Dowódca {gracz.id} ({gracz.nation})")
        self.geometry("1000x700")
        self.configure(bg="darkolivegreen")
        # Szkielet: panel mapy i panel żetonów
        self.main_frame = tk.Frame(self, bg="darkolivegreen")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.left_panel = tk.Frame(self.main_frame, width=220, bg="#556B2F")
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y)
        self.map_panel = tk.Frame(self.main_frame, bg="darkolivegreen")
        self.map_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        # Lista nowych żetonów
        tk.Label(self.left_panel, text="Nowe żetony do wystawienia:", bg="#556B2F", fg="white", font=("Arial", 12, "bold")).pack(pady=8)
        self.tokens_listbox = tk.Listbox(self.left_panel, font=("Arial", 11), width=25, height=30)
        self.tokens_listbox.pack(padx=10, pady=5, fill=tk.Y, expand=True)
        self._load_new_tokens()
        # Przycisk zamknięcia
        tk.Button(self.left_panel, text="Zamknij", command=self.destroy, bg="saddlebrown", fg="white", font=("Arial", 12, "bold")).pack(pady=10, fill=tk.X)
        # TODO: panel mapy, drag&drop, spawn_points, eksport rozmieszczenia
    def _load_new_tokens(self):
        folder = Path(f"assets/tokens/nowe_dla_{self.gracz.id}/")
        if not folder.exists():
            self.tokens_listbox.insert(tk.END, "Brak nowych żetonów.")
            return
        for sub in folder.iterdir():
            if sub.is_dir() and (sub / "token.json").exists():
                self.tokens_listbox.insert(tk.END, sub.name)
        if self.tokens_listbox.size() == 0:
            self.tokens_listbox.insert(tk.END, "Brak nowych żetonów.")
