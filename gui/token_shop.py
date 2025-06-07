import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from pathlib import Path

class TokenShop(tk.Toplevel):
    def __init__(self, parent, ekonomia, dowodcy, on_purchase_callback=None):
        super().__init__(parent)
        self.title("Zakup nowych jednostek")
        self.geometry("600x500")
        self.ekonomia = ekonomia
        self.dowodcy = dowodcy
        self.on_purchase_callback = on_purchase_callback
        self.selected_commander = tk.StringVar()
        self.points_var = tk.IntVar(value=self.ekonomia.get_points()['economic_points'])

        # Nagłówek
        tk.Label(self, text="Zakup nowych jednostek", font=("Arial", 16, "bold")).pack(pady=10)
        # Punkty ekonomiczne
        self.points_label = tk.Label(self, text=f"Dostępne punkty ekonomiczne: {self.points_var.get()}", font=("Arial", 13))
        self.points_label.pack(pady=5)
        # Wybór dowódcy
        tk.Label(self, text="Wybierz dowódcę:").pack()
        dowodcy_ids = [str(d.id) for d in self.dowodcy]
        if dowodcy_ids:
            self.selected_commander.set(dowodcy_ids[0])
        tk.OptionMenu(self, self.selected_commander, *dowodcy_ids).pack(pady=5)
        # Sekcja tworzenia żetonu (prosty formularz)
        form = tk.Frame(self)
        form.pack(pady=10)
        tk.Label(form, text="Nazwa jednostki:").grid(row=0, column=0)
        self.unit_name = tk.Entry(form)
        self.unit_name.grid(row=0, column=1)
        tk.Label(form, text="Koszt zakupu:").grid(row=1, column=0)
        self.unit_cost = tk.Entry(form)
        self.unit_cost.insert(0, "10")
        self.unit_cost.grid(row=1, column=1)
        # Przycisk kupna
        self.buy_btn = tk.Button(self, text="Kup jednostkę", command=self.buy_unit, font=("Arial", 12, "bold"), bg="#6B8E23", fg="white")
        self.buy_btn.pack(pady=10)
        # Komunikaty
        self.info_label = tk.Label(self, text="", fg="red")
        self.info_label.pack()

    def buy_unit(self):
        nazwa = self.unit_name.get().strip()
        try:
            koszt = int(self.unit_cost.get())
        except Exception:
            self.info_label.config(text="Nieprawidłowy koszt!")
            return
        if not nazwa:
            self.info_label.config(text="Podaj nazwę jednostki!")
            return
        if koszt > self.points_var.get():
            self.info_label.config(text="Za mało punktów!")
            return
        dowodca_id = self.selected_commander.get()
        # Zapisz żeton do assets/tokens/nowe_dla_{dowodca_id}/
        folder = Path("assets/tokens") / f"nowe_dla_{dowodca_id}"
        folder.mkdir(parents=True, exist_ok=True)
        # Prosty zapis: plik tekstowy z nazwą i kosztem
        idx = 1
        while (folder / f"{nazwa}_{idx}.txt").exists():
            idx += 1
        with open(folder / f"{nazwa}_{idx}.txt", "w", encoding="utf-8") as f:
            f.write(f"nazwa={nazwa}\nkoszt={koszt}\n")
        # Odejmij punkty
        self.points_var.set(self.points_var.get() - koszt)
        self.points_label.config(text=f"Dostępne punkty ekonomiczne: {self.points_var.get()}")
        self.ekonomia.subtract_points(koszt)
        self.info_label.config(text=f"Zakupiono: {nazwa} (koszt: {koszt})", fg="green")
        if self.on_purchase_callback:
            self.on_purchase_callback()
