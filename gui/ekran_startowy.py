import tkinter as tk
from tkinter import messagebox
import tkinter.simpledialog as simpledialog
from tkinter import ttk
import logging

# Konfiguracja loggera
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='ekran_startowy.log',
    filemode='w'
)

# Dodanie handlera do logowania w konsoli
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logging.getLogger().addHandler(console_handler)

class EkranStartowy:
    def __init__(self, root):
        logging.info("Inicjalizacja ekranu startowego.")
        self.root = root
        self.root.title("Ekran Startowy")
        self.root.geometry("600x400")
        self.root.configure(bg="#d3d3d3")

        self.nacje = ["Polska", "Niemcy"]
        self.miejsca = [None, None, None, None]  # Gracze 1-4
        self.stanowiska = ["Generał", "Dowódca", "Generał", "Dowódca"]

        self.create_widgets()

    def create_widgets(self):
        logging.info("Tworzenie widżetów ekranu startowego.")
        tk.Label(self.root, text="Wybór nacji i miejsc w grze", bg="#d3d3d3", font=("Arial", 16)).pack(pady=10)

        self.comboboxes = []
        for i in range(4):
            frame = tk.Frame(self.root, bg="#d3d3d3")
            frame.pack(pady=5)

            label = tk.Label(frame, text=f"Gracz {i + 1} - {self.stanowiska[i]}", bg="#d3d3d3", font=("Arial", 12))
            label.pack(side=tk.LEFT, padx=10)

            combobox = ttk.Combobox(frame, values=self.nacje, state="readonly")
            combobox.bind("<<ComboboxSelected>>", self.create_callback(i))
            combobox.pack(side=tk.LEFT)
            self.comboboxes.append(combobox)

        tk.Button(self.root, text="Rozpocznij grę", command=self.rozpocznij_gre, bg="#4CAF50", fg="white").pack(pady=20)

    def create_callback(self, idx):
        def callback(event):
            wybor = self.comboboxes[idx].get()
            self.wybierz_nacje(idx, wybor)
        return callback

    def sprawdz_wszystkie_wybory(self):
        """Weryfikuje wszystkie wybory graczy po każdej zmianie."""
        for idx, nacja in enumerate(self.miejsca):
            if idx == 0 and self.miejsca[2] and self.miejsca[0] == self.miejsca[2]:
                logging.error("Gracz 1 i Gracz 3 mają tę samą nację, co jest niezgodne z zasadami.")
                messagebox.showerror("Błąd", "Gracz 1 i Gracz 3 muszą mieć różne nacje!")
                return False
            if idx == 1 and self.miejsca[0] and self.miejsca[1] and self.miejsca[0] != self.miejsca[1]:
                logging.error("Gracz 1 i Gracz 2 mają różne nacje, co jest niezgodne z zasadami.")
                messagebox.showerror("Błąd", "Gracz 1 i Gracz 2 muszą mieć tę samą nację!")
                return False
            if idx == 3 and self.miejsca[2] and self.miejsca[3] and self.miejsca[2] != self.miejsca[3]:
                logging.error("Gracz 3 i Gracz 4 mają różne nacje, co jest niezgodne z zasadami.")
                messagebox.showerror("Błąd", "Gracz 3 i Gracz 4 muszą mieć tę samą nację!")
                return False
        return True

    def wybierz_nacje(self, idx, wybor):
        logging.debug(f"Gracz {idx + 1} wybrał nację: {wybor}")

        # Sprawdzenie, czy wybór jest pusty lub nieprawidłowy
        if not wybor or wybor not in self.nacje:
            logging.error(f"Gracz {idx + 1} wybrał nieprawidłową nację: {wybor}")
            messagebox.showerror("Błąd", "Musisz wybrać poprawną nację!")
            self.comboboxes[idx].set("")
            return

        # Zapisanie wyboru
        self.miejsca[idx] = wybor
        logging.info(f"Gracz {idx + 1} pomyślnie wybrał nację: {wybor}")

        # Weryfikacja wszystkich wyborów po zmianie
        if not self.sprawdz_wszystkie_wybory():
            self.miejsca[idx] = None
            self.comboboxes[idx].set("")

    def rozpocznij_gre(self):
        logging.info("Próba rozpoczęcia gry.")

        # Sprawdzenie poprawności wyborów przed rozpoczęciem gry
        for idx, nacja in enumerate(self.miejsca):
            if nacja is None:
                logging.error(f"Gracz {idx + 1} nie wybrał nacji.")
                messagebox.showerror("Błąd", f"Gracz {idx + 1} musi wybrać nację!")
                return

        # Dodatkowa weryfikacja logiki wyborów
        if self.miejsca[0] == self.miejsca[2]:
            logging.error("Gracz 1 i Gracz 3 mają tę samą nację, co jest niezgodne z zasadami.")
            messagebox.showerror("Błąd", "Gracz 1 i Gracz 3 muszą mieć różne nacje!")
            return

        if self.miejsca[0] != self.miejsca[1]:
            logging.error("Gracz 1 i Gracz 2 mają różne nacje, co jest niezgodne z zasadami.")
            messagebox.showerror("Błąd", "Gracz 1 i Gracz 2 muszą mieć tę samą nację!")
            return

        if self.miejsca[2] != self.miejsca[3]:
            logging.error("Gracz 3 i Gracz 4 mają różne nacje, co jest niezgodne z zasadami.")
            messagebox.showerror("Błąd", "Gracz 3 i Gracz 4 muszą mieć tę samą nację!")
            return

        logging.info("Gra się rozpoczyna.")
        messagebox.showinfo("Start", "Gra się rozpoczyna!")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = EkranStartowy(root)
    root.mainloop()