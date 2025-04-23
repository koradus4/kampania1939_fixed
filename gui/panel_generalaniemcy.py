import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk  # Obsługa obrazów
from gui.panel_pogodowy import PanelPogodowy
from gui.panel_ekonomiczny import PanelEkonomiczny
from gui.panel_gracza import PanelGracza
from gui.zarzadzanie_punktami_ekonomicznymi import ZarzadzaniePunktamiEkonomicznymi

class PanelGeneralaNiemcy(tk.Tk):
    def __init__(self, turn_number, ekonomia, gracz, gracze):
        super().__init__()
        self.title("Panel Generała Niemcy")
        self.state("zoomed")  # Maksymalizacja okna
        self.ekonomia = ekonomia  # Przechowywanie obiektu ekonomii
        self.gracze = gracze  # Przechowywanie listy graczy

        # Flaga wskazująca, czy panel jest aktywny
        self.is_active = True

        # Inicjalizacja czasu na podturę w sekundach
        self.remaining_time = gracz.czas * 60

        # Wyświetlanie numeru tury
        self.turn_label = tk.Label(self, text=f"Tura: {turn_number}", font=("Arial", 14), bg="lightgray")
        self.turn_label.pack(pady=5)

        # Główna ramka podziału
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Lewy panel (przyciski)
        self.left_frame = tk.Frame(self.main_frame, width=300, bg="olive")
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.left_frame.pack_propagate(False)  # Zapobiega dynamicznej zmianie rozmiaru panelu
        self.left_frame.config(width=298)  # Ustawia stałą szerokość panelu na 298 pikseli

        # Zastąpienie kodu odpowiedzialnego za zdjęcie i nazwisko gracza
        panel_gracza = PanelGracza(self.left_frame, "c:/Users/klif/kampania1939_fixed/gui/images/Generał pułkownik Walther von Brauchitsch.png", "Generał pułkownik Walther von Brauchitsch")
        panel_gracza.pack(pady=(10, 1), fill=tk.BOTH, expand=False)

        # Sekcja odliczania czasu
        self.timer_frame = tk.Label(self.left_frame, text=f"Pozostały czas: {self.remaining_time // 60}:{self.remaining_time % 60:02d}", font=("Arial", 14, "bold"), bg="#6B8E23", fg="white", relief=tk.RAISED, borderwidth=4, width=298, cursor="hand2")
        self.timer_frame.pack(pady=(1, 15), fill=tk.BOTH, expand=False)

        # Dodano obsługę kliknięcia na ramkę z czasem
        self.timer_frame.bind("<Button-1>", self.confirm_end_turn)

        # Dodano obsługę zmiany wyglądu przy najechaniu myszką
        self.timer_frame.bind("<Enter>", lambda e: self.timer_frame.config(bg="#556B2F"))
        self.timer_frame.bind("<Leave>", lambda e: self.timer_frame.config(bg="#6B8E23"))

        # Uruchomienie timera
        self.update_timer()

        # Dodanie klawisza "Wsparcie dowódców" z wyglądem klawisza zegara
        self.support_button = tk.Label(self.left_frame, text="Wsparcie dowódców", font=("Arial", 14, "bold"), bg="#6B8E23", fg="white", relief=tk.RAISED, borderwidth=4, width=298, cursor="hand2")
        self.support_button.pack(pady=(1, 10), fill=tk.BOTH, expand=False)

        # Dodanie obsługi kliknięcia na klawisz "Wsparcie dowódców"
        self.support_button.bind("<Button-1>", lambda e: self.show_support_sliders())

        # Dodano obsługę zmiany wyglądu przy najechaniu myszką
        self.support_button.bind("<Enter>", lambda e: self.support_button.config(bg="#556B2F"))
        self.support_button.bind("<Leave>", lambda e: self.support_button.config(bg="#6B8E23"))

        # Ukrycie suwaków na początku
        self.sliders_frame = None

        # Sekcja raportu pogodowego
        self.weather_panel = PanelPogodowy(self.left_frame)
        self.weather_panel.pack_forget()
        self.weather_panel.pack(side=tk.BOTTOM, pady=1, fill=tk.BOTH, expand=False)  # Zmniejszono przerwę między dolną częścią panelu pogodowego a dolną krawędzią okna do 1 piksela
        self.weather_panel.config(width=300, height=60)  # Ustawia stałą wysokość panelu pogodowego na 60 pikseli

        # Dodanie sekcji raportu ekonomicznego
        self.economy_panel = PanelEkonomiczny(self.left_frame)
        self.economy_panel.pack(pady=10, side=tk.BOTTOM, fill=tk.BOTH, expand=False)
        self.economy_panel.config(width=300)  # Ustawia stałą szerokość panelu ekonomicznego na 300 pikseli

        # Zmiana odstępu między panelem ekonomicznym a raportem pogodowym
        self.economy_panel.pack_configure(pady=1)

        # Filtrowanie dowódców dla danej nacji
        commanders = [gracz for gracz in gracze if gracz.nacja == "Niemcy" and gracz.rola == "Dowódca"]

        # Przekazanie dowódców do ZarzadzaniePunktamiEkonomicznymi
        self.zarzadzanie_punktami = ZarzadzaniePunktamiEkonomicznymi(
            self.left_frame,
            available_points=self.ekonomia.get_points()['economic_points'],  # Użycie rzeczywistej puli punktów ekonomicznych
            commanders=[dowodca.numer for dowodca in commanders]  # Lista dowódców dla Niemiec
        )
        self.zarzadzanie_punktami.pack_forget()

        # Prawy panel (mapa z suwakami)
        self.map_frame = tk.Frame(self.main_frame)
        self.map_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Canvas z mapą
        self.map_canvas = tk.Canvas(self.map_frame, bg="gray", scrollregion=(0, 0, 2000, 2000))
        self.map_canvas.grid(row=0, column=0, sticky="nsew")
        self.map_canvas.config(scrollregion=(0, 0, 0, 0))  # Usuwa suwaki

        # Suwaki
        self.h_scroll = tk.Scrollbar(self.map_frame, orient=tk.HORIZONTAL, command=self.map_canvas.xview)
        self.h_scroll.grid(row=1, column=0, sticky="ew")
        self.v_scroll = tk.Scrollbar(self.map_frame, orient=tk.VERTICAL, command=self.map_canvas.yview)
        self.v_scroll.grid(row=0, column=1, sticky="ns")

        self.map_canvas.config(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)

        # Konfiguracja siatki w map_frame
        self.map_frame.grid_rowconfigure(0, weight=1)
        self.map_frame.grid_columnconfigure(0, weight=1)

        self.map_canvas.bind("<Configure>", self.update_scrollregion)

        # Wczytanie mapy
        self.load_map("gui/mapa_cyfrowa/mapa_globalna.jpg")

        # Obsługa przesuwania myszką
        self.map_canvas.bind("<ButtonPress-1>", self.start_pan)
        self.map_canvas.bind("<B1-Motion>", self.do_pan)

    def load_map(self, map_path):
        """Wczytuje mapę i wyświetla ją na canvasie."""
        try:
            self.map_image = Image.open(map_path)
            self.map_photo = ImageTk.PhotoImage(self.map_image)
            self.map_canvas.create_image(0, 0, anchor="nw", image=self.map_photo)
        except Exception as e:
            print(f"Nie udało się wczytać mapy: {e}")

    def start_pan(self, event):
        """Rozpoczyna przesuwanie mapy myszką."""
        self.map_canvas.scan_mark(event.x, event.y)

    def do_pan(self, event):
        """Przesuwa mapę myszką."""
        self.map_canvas.scan_dragto(event.x, event.y, gain=1)

    def update_scrollregion(self, event):
        """Aktualizuje obszar przewijania mapy."""
        self.map_canvas.config(scrollregion=self.map_canvas.bbox("all"))

    def end_turn(self):
        """Kończy podturę."""
        self.destroy()

    def destroy(self):
        if hasattr(self, 'timer_id'):
            self.after_cancel(self.timer_id)
        self.is_active = False  # Ustawienie flagi na False przy niszczeniu panelu
        super().destroy()

    def update_weather(self, weather_report):
        """Aktualizuje sekcję raportu pogodowego w panelu."""
        self.weather_panel.update_weather(weather_report)

    def update_economy(self):
        """Aktualizuje sekcję raportu ekonomicznego w panelu oraz wartość dostępnych punktów w suwakach."""
        economy_report = f"Punkty ekonomiczne: {self.ekonomia.get_points()['economic_points']}\nPunkty specjalne: {self.ekonomia.get_points()['special_points']}"
        self.economy_panel.update_economy(economy_report)

        # Aktualizacja dostępnych punktów w suwakach
        new_available_points = self.ekonomia.get_points()['economic_points']
        self.zarzadzanie_punktami.refresh_available_points(new_available_points)

    def update_timer(self):
        """Aktualizuje odliczanie czasu."""
        if self.winfo_exists():
            if self.remaining_time > 0:
                self.remaining_time -= 1
                self.timer_frame.config(text=f"Pozostały czas: {self.remaining_time // 60}:{self.remaining_time % 60:02d}")
                self.timer_id = self.after(1000, self.update_timer)
            else:
                self.end_turn()

    def confirm_end_turn(self, event):
        """Potwierdza zakończenie tury."""
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz zakończyć turę przed czasem?"):
            self.end_turn()

    def show_support_sliders(self):
        # Ukrycie klawisza "Wsparcie dowódców"
        self.support_button.pack_forget()

        # Resetowanie wartości suwaków do 0 przy każdym otwarciu sekcji
        for commander in self.zarzadzanie_punktami.commander_points.keys():
            slider = getattr(self.zarzadzanie_punktami, f"{commander}_slider", None)
            if slider:
                slider.set(0)
            self.zarzadzanie_punktami.commander_points[commander] = 0

        # Wyświetlenie suwaków
        self.zarzadzanie_punktami.pack(pady=10, fill=tk.BOTH, expand=False)

        # Dodanie przycisku "Akceptuj" tylko raz
        if not hasattr(self, 'accept_button'):
            self.accept_button = tk.Button(self.zarzadzanie_punktami, text="Akceptuj", font=("Arial", 14, "bold"), bg="#6B8E23", fg="white", command=self.accept_support)
            self.accept_button.pack(pady=10, fill=tk.BOTH, expand=False)

    def accept_support(self):
        # Debug: Wyświetlenie przydzielonych punktów
        print("[DEBUG] Przydzielone punkty:")
        for commander, points in self.zarzadzanie_punktami.commander_points.items():
            print(f"[DEBUG] Dowódca {commander}: {points} punktów")

        # Przekazanie punktów do dowódców
        for commander_id, pts in self.zarzadzanie_punktami.commander_points.items():
            if pts > 0:
                for player in self.gracze:  # Iteracja po liście graczy
                    if player.numer == commander_id and player.rola == "Dowódca":
                        player.economy.economic_points += pts
                        print(f"[DEBUG] Dowódca {commander_id} otrzymał {pts} punktów. Aktualna suma: {player.economy.economic_points}")

        # Debug: Wyświetlenie sumy punktów przekazanych do zarządzania ekonomią
        total_assigned_points = sum(self.zarzadzanie_punktami.commander_points.values())
        print(f"[DEBUG] Suma punktów przekazanych do zarządzania ekonomią: {total_assigned_points}")

        # Aktualizacja raportu ekonomicznego po rozdysponowaniu punktów
        self.ekonomia.subtract_points(total_assigned_points)
        self.update_economy()

        # Ukrycie suwaków
        self.zarzadzanie_punktami.pack_forget()

        # Przywrócenie klawisza "Wsparcie dowódców"
        self.support_button.pack(pady=(1, 10), fill=tk.BOTH, expand=False)

if __name__ == "__main__":
    app = PanelGeneralaNiemcy(turn_number=1, ekonomia=None, gracz=None, gracze=[])  # Przekazanie obiektu gracza i listy graczy
    app.mainloop()