# UNIWERSALNY TWÓRCA ARMII - WSZYSTKIE DOWÓDCY

## Przegląd

Automatycznie tworzy armie dla **wszystkich 4 dowódców** w grze Kampania 1939:
- **Dowódca 2 (Polska)** - Armia Górska  
- **Dowódca 3 (Polska)** - Armia Kawalerii
- **Dowódca 5 (Niemcy)** - Panzer Division
- **Dowódca 6 (Niemcy)** - Infantry Division

## Uruchomienie

```bash
python tools/army_automation/universal_army_creator.py
```

## Utworzone Armie

### 🎖️ Dowódca 2 (Polska) - Armia Górska (172 VP)
- **2. Batalion Piechoty Górskiej** (45 VP) - Elitarna piechota z przewodnikami
- **2. Dywizjon Artylerii Ciężkiej** (50 VP) - Potężna artyleria dalekiego zasięgu  
- **2. Pluton Czołgów Średnich** (40 VP) - Pancerne wsparcie
- **2. Kompania Samochodów Pancernych** (35 VP) - Szybkie rozpoznanie

### 🎖️ Dowódca 3 (Polska) - Armia Kawalerii (160 VP)
- **3. Pułk Ułanów Krakowskich** (35 VP) - Szybka kawaleria z szablami
- **3. Batalion Strzelców Podhalańskich** (40 VP) - Górska piechota ze snajperami
- **3. Bateria Artylerii Konnej** (42 VP) - Mobilna artyleria  
- **3. Pluton Tankietek** (25 VP) - Lekkie czołgi rozpoznawcze
- **3. Oddział Rozpoznawczy** (18 VP) - Wywiad i obserwacja

### 🎖️ Dowódca 5 (Niemcy) - Panzer Division (208 VP)
- **5. Panzergrenadier Regiment** (48 VP) - Zmotoryzowana piechota
- **5. Panzer Abteilung** (60 VP) - Ciężkie czołgi Panzer IV
- **5. Artillerie Regiment** (70 VP) - Artyleria batalionu leFH 18
- **5. Aufklärungs Abteilung** (30 VP) - Pancerne rozpoznanie

### 🎖️ Dowódca 6 (Niemcy) - Infantry Division (170 VP)  
- **6. Infanterie Regiment** (42 VP) - Standardowa piechota z MG 34
- **6. Panzer Kompanie** (38 VP) - Lekkie czołgi Panzer II
- **6. leichte Artillerie** (36 VP) - Lekka artyleria leIG 18
- **6. Flak Abteilung** (32 VP) - Obrona przeciwlotnicza Flak 38
- **6. Pionier Zug** (22 VP) - Saperzy z ładunkami wybuchowymi

## Balans Armii

### Polskie (332 VP łącznie)
- **Mobilność:** Wysoka (kawaleria, tankietki)
- **Specjalizacja:** Walka w górach, rozpoznanie
- **Wsparcie:** Przewodnicy, snajperzy, wywiad

### Niemieckie (378 VP łącznie)  
- **Siła ognia:** Bardzo wysoka (ciężka artyleria, Panzer IV)
- **Technologia:** Nowoczesne (Sd.Kfz., MG 34, Flak)
- **Taktyka:** Combined arms, blitzkrieg

## Struktura Plików

Po uruchomieniu skryptu zostaną utworzone:

```
assets/tokens/
├── index.json (zaktualizowany z wszystkimi żetonami)
├── Polska/
│   ├── [żetony dowódcy 2]/
│   └── [żetony dowódcy 3]/
└── Niemcy/  
    ├── [żetony dowódcy 5]/
    └── [żetony dowódcy 6]/
```

Każdy żeton zawiera:
- `token.json` - pełne dane jednostki
- `token.png` - grafika 240x240 px

## Funkcje

✅ **Prawdziwa automatyzacja Token Editor**  
✅ **Historycznie poprawne nazwy jednostek**  
✅ **Zbalansowane statystyki**  
✅ **Różnorodne typy jednostek**  
✅ **Realistyczne wsparcie**  
✅ **Automatyczna weryfikacja**  

## Czas Wykonania

Około **2-3 minuty** na wszystkie 4 armie (18 żetonów).

---

*Narzędzie stworzone dla projektu Kampania 1939*
