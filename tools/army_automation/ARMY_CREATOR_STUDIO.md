# 🎖️ ARMY CREATOR STUDIO - Instrukcja Obsługi

## Przegląd

**Army Creator Studio** to zaawansowana aplikacja GUI do profesjonalnego tworzenia armii w grze Kampania 1939. Oferuje pełną kontrolę nad parametrami armii i automatyczne generowanie zbalansowanych jednostek.

## Uruchomienie

```bash
python tools/army_automation/army_creator_studio.py
```

## Interfejs Użytkownika

### 📊 Panel Parametrów (Lewa strona)

#### ⚙️ Podstawowe Ustawienia
- **🏴 Nacja**: Wybór między Polską a Niemcami
- **👨‍✈️ Dowódca**: Automatyczny wybór dostępnych dowódców dla nacji

#### 📈 Parametry Armii  
- **📊 Ilość żetonów**: Suwak 5-25 jednostek
- **💰 Budżet VP**: Suwak 250-1000 VP
- **Podgląd na żywo**: Automatyczne obliczanie ~VP/żeton

#### 🎮 Narzędzia Generowania
- **🎲 Losowa Armia**: Generuje losowe parametry
- **⚖️ Zbalansuj Auto**: Optymalizuje proporcje VP/żetony
- **🗑️ Wyczyść**: Czyści podgląd armii

#### 💾 Tworzenie
- **💾 UTWÓRZ ARMIĘ**: Główny przycisk - rozpoczyna proces

### 👁️ Panel Podglądu (Prawa strona)

#### 📋 Podgląd Składu
- **Lista jednostek**: Real-time podgląd armii
- **Statystyki**: Suma VP, pozostały budżet
- **Analiza balansu**: Procentowy rozkład typów jednostek

#### ⏳ Monitoring Postępu
- **Progress bar**: Wizualny postęp tworzenia
- **Status**: Aktualna operacja
- **Podsumowanie**: Raport końcowy

## Funkcje Zaawansowane

### 🧠 Inteligentne Balansowanie

Aplikacja używa algorytmu balansowania opartego na wagach:

- **Piechota (40%)**: Podstawa każdej armii
- **Pancerne (30%)**: Siła uderzeniowa  
- **Artyleria (20%)**: Wsparcie ogniowe
- **Wsparcie (10%)**: Rozpoznanie, dowództwo

### 🎯 Adaptacyjne Koszty

- **Rozmiar jednostki**: Pluton (1.0x) → Kompania (1.5x) → Batalion (2.2x)
- **Wariacja kosztów**: ±20% dla realizmu
- **Optymalizacja budżetu**: Maksymalne wykorzystanie VP

### 🏗️ Inteligentne Nazwy

#### Polskie Jednostki:
- `2. Pułk Piechoty`
- `3. Batalion Strzelców`  
- `1. Szwadron Ułanów`
- `2. Bateria Artylerii`

#### Niemieckie Jednostki:
- `5. Infanterie Regiment`
- `6. Panzer Kompanie`
- `5. Artillerie Abteilung`
- `6. Aufklärungs Zug`

## Proces Tworzenia Armii

### 1️⃣ Konfiguracja
1. Wybierz **nację** i **dowódcę**
2. Ustaw **ilość żetonów** (5-25)
3. Ustaw **budżet VP** (250-1000)

### 2️⃣ Optymalizacja
1. Użyj **🎲 Losowa Armia** dla inspiracji
2. Użyj **⚖️ Zbalansuj Auto** dla optymalnych proporcji
3. Obserwuj **podgląd na żywo**

### 3️⃣ Tworzenie  
1. Kliknij **💾 UTWÓRZ ARMIĘ**
2. Obserwuj **progress bar**
3. Poczekaj na **podsumowanie**

### 4️⃣ Rezultat
✅ Żetony w `assets/tokens/[Nacja]/`  
✅ Pliki JSON + PNG (240x240)  
✅ Zaktualizowany index.json  
✅ Historycznie poprawne nazwy  

## Przykłady Użycia

### 🎯 Szybka Armia
```
Nacja: Polska
Dowódca: 2 (Polska)
Żetony: 10
VP: 400
```
➡️ **⚖️ Zbalansuj Auto** ➡️ **💾 UTWÓRZ ARMIĘ**

### 🏴‍☠️ Mega Armia
```
Nacja: Niemcy  
Dowódca: 5 (Niemcy)
Żetony: 25
VP: 1000
```
➡️ **🎲 Losowa Armia** ➡️ dostosuj ➡️ **💾 UTWÓRZ ARMIĘ**

### 🎪 Eksperymentalna
```
Nacja: Polska
Dowódca: 3 (Polska)  
Żetony: 7
VP: 250
```
➡️ Ręczne ustawienia ➡️ **💾 UTWÓRZ ARMIĘ**

## Automatyzacja i Bezpieczeństwo

### ✅ W pełni automatyczne:
- **Bez dialogów potwierdzających**
- **Bez otwierania Token Editor GUI**
- **Bez ręcznego zamykania okien**
- **Automatyczne mockowanie systemowych dialogów**

### 🛡️ Bezpieczne:
- **Osobne katalogi** dla każdego żetonu
- **Unikalne ID** - brak nadpisywania
- **Validation** - sprawdzanie błędów
- **Graceful failure** - obsługa wyjątków

## Wymagania Techniczne

- **Python 3.7+**
- **Tkinter** (zwykle wbudowany)
- **Pillow** (do grafik PNG)
- **PathLib** (do zarządzania ścieżkami)

## Status i Monitoring

### 📊 Progress Bar
- **Inicjalizacja**: Ładowanie Token Editor
- **Tworzenie**: Postęp żeton po żetonie
- **Zakończenie**: Podsumowanie i statystyki

### 📱 Status Bar
- **⚡ Gotowy**: Aplikacja gotowa do użycia
- **🏭 Tworzenie**: Proces w toku
- **🎉 Ukończono**: Sukces + liczba żetonów
- **❌ Błąd**: Informacja o problemie

---

**🎖️ Army Creator Studio - Profesjonalne narzędzie dla Kampanii 1939**

*Szybko, łatwo, automatycznie!* 🚀
