import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from gui.panel_pogodowy import PanelPogodowy
from gui.panel_gracza import PanelGracza

class PanelDowodcy:
    def __init__(self, turn_number, remaining_time, gracz):
        self.turn_number = turn_number
        self.remaining_time = remaining_time
        self.gracz = gracz

        # Tworzenie głównego okna
        self.root = tk.Tk()
        self.root.title(f"Panel Dowódcy - {self.gracz.nacja}")
        self.root.state("zoomed")

        # Wyświetlanie numeru tury
        self.turn_label = tk.Label(self.root, text=f"Tura: {self.turn_number}", font=("Arial", 14), bg="lightgray")
        self.turn_label.pack(pady=5)

        # Główna ramka podziału
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Lewy panel (przyciski)
        self.left_frame = tk.Frame(self.main_frame, width=300, bg="olive")
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.left_frame.pack_propagate(False)

        # Panel gracza
        panel_gracza = PanelGracza(self.left_frame, self.gracz.name, self.gracz.image_path)
        panel_gracza.pack(pady=(10, 1), fill=tk.BOTH, expand=False)

        # Sekcja odliczania czasu
        self.timer_frame = tk.Label(self.left_frame, text=f"Pozostały czas: {self.remaining_time // 60}:{self.remaining_time % 60:02d}", font=("Arial", 14, "bold"), bg="#6B8E23", fg="white", relief=tk.RAISED, borderwidth=4)
        self.timer_frame.pack(pady=(1, 15), fill=tk.BOTH, expand=False)

        # Dodanie obsługi kliknięcia na ramkę z czasem
        self.timer_frame.bind("<Button-1>", self.confirm_end_turn)

        # Punkty ekonomiczne
        self.points_frame = tk.Label(self.left_frame, text="Punkty do odbioru: 0", font=("Arial", 14, "bold"), bg="#6B8E23", fg="white", relief=tk.RAISED, borderwidth=4)
        self.points_frame.pack(pady=(1, 10), fill=tk.BOTH, expand=False)

        # Panel pogodowy
        self.weather_panel = PanelPogodowy(self.left_frame)
        self.weather_panel.pack(pady=10, side=tk.BOTTOM, fill=tk.BOTH, expand=False)

        # Prawy panel (mapa)
        self.map_frame = tk.Frame(self.main_frame)
        self.map_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.map_canvas = tk.Canvas(self.map_frame, bg="gray", scrollregion=(0, 0, 2000, 2000))
        self.map_canvas.grid(row=0, column=0, sticky="nsew")

        self.h_scroll = tk.Scrollbar(self.map_frame, orient=tk.HORIZONTAL, command=self.map_canvas.xview)
        self.h_scroll.grid(row=1, column=0, sticky="ew")
        self.v_scroll = tk.Scrollbar(self.map_frame, orient=tk.VERTICAL, command=self.map_canvas.yview)
        self.v_scroll.grid(row=0, column=1, sticky="ns")

        self.map_canvas.config(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)
        self.map_frame.grid_rowconfigure(0, weight=1)
        self.map_frame.grid_columnconfigure(0, weight=1)

        self.map_canvas.bind("<Configure>", self.update_scrollregion)
        self.map_canvas.bind("<ButtonPress-1>", self.start_pan)
        self.map_canvas.bind("<B1-Motion>", self.do_pan)

        self.load_map()
        self.update_timer()

    def load_map(self):
        global_map_path = "C:/Users/klif/kampania1939_fixed/edytory/assets/mapa_globalna.jpg"
        try:
            self.map_image = Image.open(global_map_path)
            self.map_photo = ImageTk.PhotoImage(self.map_image)
            self.map_canvas.create_image(0, 0, anchor="nw", image=self.map_photo)
        except Exception as e:
            print(f"Nie udało się wczytać mapy: {e}")

    def start_pan(self, event):
        self.map_canvas.scan_mark(event.x, event.y)

    def do_pan(self, event):
        self.map_canvas.scan_dragto(event.x, event.y, gain=1)

    def update_scrollregion(self, event):
        self.map_canvas.config(scrollregion=self.map_canvas.bbox("all"))

    def update_timer(self):
        if self.root.winfo_exists():
            if self.remaining_time > 0:
                self.remaining_time -= 1
                self.timer_frame.config(text=f"Pozostały czas: {self.remaining_time // 60}:{self.remaining_time % 60:02d}")
                self.timer_id = self.root.after(1000, self.update_timer)  # Przypisanie identyfikatora timera
            else:
                self.destroy()

    def update_weather(self, weather_report):
        self.weather_panel.update_weather(weather_report)

    def update_economy(self, points):
        self.points_frame.config(text=f"Punkty do odbioru: {points}")

    def confirm_end_turn(self, event):
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz zakończyć turę przed czasem?"):
            self.destroy()

    def end_turn(self):
        self.destroy()

    def destroy(self):
        """Anuluje timer i niszczy okno."""
        if hasattr(self, 'timer_id') and self.timer_id is not None:
            try:
                self.root.after_cancel(self.timer_id)
                self.timer_id = None  # Resetowanie identyfikatora timera
            except Exception as e:
                print(f"[ERROR] Nie udało się anulować timera: {e}")
        self.root.destroy()

    def mainloop(self):
        self.root.mainloop()