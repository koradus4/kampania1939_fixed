import tkinter as tk
from PIL import Image, ImageTk

class PanelGracza(tk.Frame):
    _instances = []  # Lista wszystkich instancji PanelGracza

    def __init__(self, parent, name, image_path, game_engine, player=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.game_engine = game_engine
        self.player = player
        PanelGracza._instances.append(self)  # Rejestracja instancji

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
            self.image = Image.new("RGB", (298, 298), color="gray")  # Domyślne szare tło w przypadku błędu
        self.photo = ImageTk.PhotoImage(self.image)
        self.photo_label = tk.Label(self.photo_frame, image=self.photo, bg="white")
        self.photo_label.place(x=0, y=0, width=298, height=298)

        # --- DODANE: okno 110x80 px w prawym górnym rogu zdjęcia ---
        # Prostokąt 110x80, 1 piksel od górnej i prawej ramki zdjęcia
        self.overlay_frame = tk.Frame(self.photo_frame, bg="lightgray", relief=tk.RAISED, borderwidth=2)
        self.overlay_frame.place(x=298-110-1, y=1, width=110, height=80)  # Zwiększona szerokość

        # --- WIDGET VP ---
        # Etykieta "Punkty zwycięstwa (nacja)" na górze overlay
        self.vp_label = tk.Label(self.overlay_frame, text="Punkty zwycięstwa (nacja)", font=("Arial", 8, "bold"), bg="lightgray", wraplength=105, justify=tk.CENTER)
        self.vp_label.pack(side=tk.TOP, pady=(4, 2))
        # Białe pole z wartością VP (szersze)
        self.vp_value_box = tk.Frame(self.overlay_frame, bg="white", relief=tk.SUNKEN, borderwidth=2, width=90, height=32)
        self.vp_value_box.pack(side=tk.TOP, pady=(2, 4))
        self.vp_value_box.pack_propagate(False)
        self.vp_value_label = tk.Label(self.vp_value_box, text="0", font=("Arial", 20, "bold"), bg="white", fg="black")
        self.vp_value_label.pack(expand=True, fill=tk.BOTH)

        # --- METODA AKTUALIZACJI VP ---
        PanelGracza.update_all_vp()

        # Przyciski ZAPISZ/WCZYTAJ GRĘ pod zdjęciem
        btn_frame = tk.Frame(self, bg="white")
        btn_frame.pack(pady=8)

        from tkinter import messagebox, filedialog
        from engine.save_manager import save_game, load_game

        def on_save():
            import os
            from datetime import datetime
            saves_dir = os.path.join(os.getcwd(), 'saves')
            os.makedirs(saves_dir, exist_ok=True)
            # Pobierz dane gracza do nazwy pliku
            p = self.player
            if p is None:
                # Spróbuj pobrać z game_engine (fallback, jeśli nie przekazano player)
                p = getattr(self.game_engine, 'current_player', None)
                if p is None and hasattr(self.game_engine, 'current_player_obj'):
                    p = self.game_engine.current_player_obj
            role = getattr(p, 'role', 'Gracz') if p else 'Gracz'
            nation = getattr(p, 'nation', '') if p else ''
            player_id = getattr(p, 'id', '') if p else ''
            role = str(role).replace(' ', '_')
            nation = str(nation).replace(' ', '_')
            player_id = str(player_id)
            default_name = f"save_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{role}{player_id}_{nation}.json"
            path = filedialog.asksaveasfilename(
                defaultextension='.json',
                filetypes=[('Plik zapisu', '*.json')],
                initialdir=saves_dir,
                initialfile=default_name
            )
            if not path:
                # Jeśli użytkownik anuluje, nie zapisuj
                return
            try:
                save_game(path, self.game_engine, self.player)
                from tkinter import messagebox
                messagebox.showinfo("Zapis gry", f"Gra została zapisana jako:\n{os.path.basename(path)}")
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("Błąd zapisu", str(e))

        def on_load():
            import os
            saves_dir = os.path.join(os.getcwd(), 'saves')
            os.makedirs(saves_dir, exist_ok=True)
            path = filedialog.askopenfilename(
                filetypes=[('Plik zapisu', '*.json')],
                initialdir=saves_dir
            )
            if path:
                try:
                    # Wczytaj grę i pobierz info o aktywnym graczu
                    from engine.save_manager import load_game
                    active_player_info = load_game(path, self.game_engine)
                    # Odśwież panele
                    if hasattr(self.master, 'panel_mapa'):
                        self.master.panel_mapa.refresh()
                    # --- Nowość: automatyczne przełączanie panelu na gracza z save ---
                    if active_player_info:
                        # Przekaż info do głównej pętli lub wywołaj callback (tu: komunikat)
                        msg = f"Gra została wczytana!\nAktywny gracz: {active_player_info.get('role','?')} {active_player_info.get('id','?')} ({active_player_info.get('nation','?')})"
                        messagebox.showinfo("Wczytanie gry", msg)
                    else:
                        messagebox.showinfo("Wczytanie gry", "Gra została wczytana!")
                    # --- Aktualizacja VP po wczytaniu gry ---
                    PanelGracza.update_all_vp()
                except Exception as e:
                    messagebox.showerror("Błąd wczytywania", str(e))

        self.on_load = on_load
        self.btn_save = tk.Button(btn_frame, text="Zapisz grę", command=on_save, bg="saddlebrown", fg="white", font=("Arial", 11, "bold"), width=12)
        self.btn_save.pack(side=tk.LEFT, padx=6)
        self.btn_load = tk.Button(btn_frame, text="Wczytaj grę", command=self.on_load, bg="saddlebrown", fg="white", font=("Arial", 11, "bold"), width=12)
        self.btn_load.pack(side=tk.LEFT, padx=6)

    @classmethod
    def update_all_vp(cls):
        for inst in cls._instances:
            inst.update_vp()

    def get_nation_vp(self):
        """Zwraca sumę punktów zwycięstwa dla nacji tego gracza."""
        if not self.player or not hasattr(self.player, 'nation'):
            return 0
        nation = self.player.nation
        # Pobierz listę graczy z game_engine
        players = getattr(self.game_engine, 'players', None)
        if not players:
            # fallback: tylko ten gracz
            return getattr(self.player, 'victory_points', 0)
        return sum(getattr(p, 'victory_points', 0) for p in players if getattr(p, 'nation', None) == nation)

    def update_vp(self):
        """Aktualizuje wyświetlaną wartość punktów zwycięstwa (VP) dla nacji gracza."""
        vp = self.get_nation_vp()
        # Automatyczne skalowanie czcionki dla dużych liczb
        if len(str(vp)) >= 4:
            font = ("Arial", 14, "bold")
        else:
            font = ("Arial", 20, "bold")
        self.vp_value_label.config(text=str(vp), font=font)

    def destroy(self):
        # Usuwanie instancji z rejestru przy zamknięciu
        if self in PanelGracza._instances:
            PanelGracza._instances.remove(self)
        super().destroy()

# Testowanie modułu
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Test Panelu Gracza")
    panel = PanelGracza(root, "Marszałek Polski Edward Rydz-Śmigły", "C:/Users/klif/kampania1939_fixed/assets/mapa_globalna.jpg", None)
    panel.pack(pady=20, padx=20)
    root.mainloop()