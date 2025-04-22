import tkinter as tk

class ZarzadzaniePunktamiEkonomicznymi(tk.Frame):
    def __init__(self, parent, available_points, commanders, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.available_points = available_points  # Dostępna pula punktów ekonomicznych
        self.commanders = commanders  # Lista dowódców
        self.commander_points = {commander: 0 for commander in commanders}  # Punkty przydzielone dowódcom

        # Wyświetlanie dostępnych punktów
        self.points_label = tk.Label(self, text=f"Dostępne punkty: {self.available_points}", font=("Arial", 12))
        self.points_label.pack(pady=5)

        # Tworzenie suwaków dla każdego dowódcy
        for commander in self.commanders:
            frame = tk.Frame(self)
            frame.pack(fill=tk.X, pady=5)

            label = tk.Label(frame, text=commander, font=("Arial", 10))
            label.pack(side=tk.LEFT, padx=5)

            slider = tk.Scale(frame, from_=0, to=self.available_points, orient=tk.HORIZONTAL, resolution=1, command=lambda value, c=commander: self.update_points(c, int(value)))
            slider.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

            setattr(self, f"{commander}_slider", slider)

    def update_points(self, commander, value):
        # Obliczanie nowej dostępnej puli punktów
        current_total = sum(self.commander_points.values()) - self.commander_points[commander]
        if current_total + value <= self.available_points:
            self.commander_points[commander] = value
            self.points_label.config(text=f"Dostępne punkty: {self.available_points - sum(self.commander_points.values())}")
        else:
            # Przywracanie suwaka do poprzedniej wartości, jeśli przekroczono limit
            slider = getattr(self, f"{commander}_slider")
            slider.set(self.commander_points[commander])

    def refresh_available_points(self, new_available_points):
        """Aktualizuje dostępną pulę punktów ekonomicznych."""
        self.available_points = new_available_points
        self.points_label.config(text=f"Dostępne punkty: {self.available_points - sum(self.commander_points.values())}")

        # Aktualizacja zakresu suwaków
        for commander in self.commanders:
            slider = getattr(self, f"{commander}_slider")
            slider.config(to=self.available_points)

        # Usunięcie nadmiarowego suwaka, jeśli liczba dowódców jest mniejsza niż liczba suwaków
        for commander in list(self.commander_points.keys()):
            if commander not in self.commanders:
                del self.commander_points[commander]
                slider = getattr(self, f"{commander}_slider", None)
                if slider:
                    slider.destroy()

        # Dodanie brakujących suwaków, jeśli dowódcy zostali zmienieni
        for commander in self.commanders:
            if commander not in self.commander_points:
                self.commander_points[commander] = 0
                frame = tk.Frame(self)
                frame.pack(fill=tk.X, pady=5)

                label = tk.Label(frame, text=commander, font=("Arial", 10))
                label.pack(side=tk.LEFT, padx=5)

                slider = tk.Scale(frame, from_=0, to=self.available_points, orient=tk.HORIZONTAL, resolution=1, command=lambda value, c=commander: self.update_points(c, int(value)))
                slider.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

                setattr(self, f"{commander}_slider", slider)

    def accept_final_points(self):
        """Zapisuje finalne ustawienia suwaków po akceptacji."""
        for commander in self.commanders:
            slider = getattr(self, f"{commander}_slider", None)
            if slider:
                self.commander_points[commander] = slider.get()

        # Debug: Wyświetlenie finalnych punktów po akceptacji
        print("[DEBUG] Finalne ustawienia punktów:")
        for commander, points in self.commander_points.items():
            print(f"[DEBUG] Dowódca {commander}: {points} punktów")