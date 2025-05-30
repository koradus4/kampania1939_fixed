class Player:
    def __init__(self, player_id, nation, role, time_limit=5, image_path=None, economy=None):
        self.id = player_id
        self.nation = nation
        self.role = role  # np. "Generał", "Dowódca"
        self.time_limit = time_limit  # czas na turę/podturę
        self.economy = economy  # obiekt ekonomii, jeśli wymagany

        # Domyślne ścieżki do obrazów
        base_path = "c:/Users/klif/kampania1939_fixed/gui/images/"
        if image_path is not None:
            self.image_path = image_path
        else:
            if self.nation == "Polska" and self.role == "Generał":
                self.image_path = base_path + "Marszałek Polski Edward Rydz-Śmigły.png"
            elif self.nation == "Niemcy" and self.role == "Generał":
                self.image_path = base_path + "Generał pułkownik Walther von Brauchitsch.png"
            elif self.nation == "Polska" and self.role == "Dowódca":
                if self.id == 2:
                    self.image_path = base_path + "Generał Juliusz Rómmel.png"
                else:
                    self.image_path = base_path + "Generał Tadeusz Kutrzeba.png"
            elif self.nation == "Niemcy" and self.role == "Dowódca":
                if self.id == 6:
                    self.image_path = base_path + "Generał Walther von Reichenau.png"
                else:
                    self.image_path = base_path + "Generał Fedor von Bock.png"
            else:
                self.image_path = base_path + "default.png"

        # Domyślne ścieżki do map
        if self.nation == "Polska" and self.role == "Generał":
            self.map_path = "C:/Users/klif/kampania1939_fixed/assets/mapa_globalna.jpg"
        elif self.nation == "Niemcy" and self.role == "Generał":
            self.map_path = "C:/Users/klif/kampania1939_fixed/assets/mapa_globalna.jpg"
        elif self.nation == "Polska" and self.role == "Dowódca":
            if self.id == 2:
                self.map_path = "c:/Users/klif/kampania1939_fixed/gui/mapa_cyfrowa/mapa_dowodca2.jpg"
            else:
                self.map_path = "c:/Users/klif/kampania1939_fixed/gui/mapa_cyfrowa/mapa_dowodca1.jpg"
        elif self.nation == "Niemcy" and self.role == "Dowódca":
            if self.id == 6:
                self.map_path = "c:/Users/klif/kampania1939_fixed/gui/mapa_cyfrowa/mapa_dowodca2.jpg"
            else:
                self.map_path = "c:/Users/klif/kampania1939_fixed/gui/mapa_cyfrowa/mapa_dowodca1.jpg"
        else:
            self.map_path = "c:/Users/klif/kampania1939_fixed/gui/mapa_cyfrowa/mapa_hex.jpg"

        # Domyślna nazwa gracza
        if self.nation == "Polska" and self.role == "Generał":
            self.name = "Marszałek Polski Edward Rydz-Śmigły"
        elif self.nation == "Niemcy" and self.role == "Generał":
            self.name = "Generał pułkownik Walther von Brauchitsch"
        elif self.nation == "Polska" and self.role == "Dowódca":
            if self.id == 2:
                self.name = "Generał Juliusz Rómmel"
            else:
                self.name = "Generał Tadeusz Kutrzeba"
        elif self.nation == "Niemcy" and self.role == "Dowódca":
            if self.id == 6:
                self.name = "Generał Walther von Reichenau"
            else:
                self.name = "Generał Fedor von Bock"
        else:
            self.name = f"Player {self.id}"

        self.visible_hexes = set()  # Heksy widoczne dla gracza
        self.visible_tokens = set()  # ID żetonów widocznych dla gracza

    def serialize(self):
        return {
            'id': self.id,
            'nation': self.nation,
            'role': self.role,
            'name': self.name,
            'time_limit': self.time_limit,
            'image_path': self.image_path,
            'map_path': self.map_path
        }

    def __str__(self):
        return f"Player {self.id}: {self.nation} - {self.role} - {self.name}"
