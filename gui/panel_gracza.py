import tkinter as tk
from PIL import Image, ImageTk

class PanelGracza(tk.Frame):
    def __init__(self, parent, name, image_path, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Ramka na nazwisko
        self.name_label = tk.Label(self, text=name, font=("Arial", 12), bg="white", relief=tk.SUNKEN, borderwidth=2, wraplength=280, justify=tk.CENTER, height=2)
        self.name_label.pack(pady=5, fill=tk.BOTH, expand=False)

        # Ramka na zdjęcie
        self.photo_frame = tk.Frame(self, width=298, height=298, bg="white", relief=tk.SUNKEN, borderwidth=2)
        self.photo_frame.pack(pady=10, fill=tk.BOTH, expand=False)

        # Wczytanie zdjęcia gracza i dopasowanie do ramki
        try:
            self.image = Image.open(image_path).resize((298, 298), Image.Resampling.LANCZOS)
        except Exception as e:
            print(f"[ERROR] Nie udało się wczytać zdjęcia gracza: {e}")
            self.image = Image.new("RGB", (298, 298), color="gray")  # Domyślne szare tło w przypadku błędu
        self.photo = ImageTk.PhotoImage(self.image)
        self.photo_label = tk.Label(self.photo_frame, image=self.photo, bg="white")
        self.photo_label.image = self.photo  # Referencja, aby obraz nie został usunięty przez GC
        self.photo_label.pack()

# Testowanie modułu
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Test Panelu Gracza")
    panel = PanelGracza(root, "Marszałek Polski Edward Rydz-Śmigły", "C:/Users/klif/kampania1939_fixed/assets/mapa_globalna.jpg")
    panel.pack(pady=20, padx=20)
    root.mainloop()