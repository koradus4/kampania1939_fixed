# AUTOMATYZACJA ARMII - NARZĘDZIA

Ten folder zawiera gotowe narzędzia do automatycznego tworzenia armii za pomocą Token Editor.

## Zawartość

### `army_creator_studio.py` ⭐ **GŁÓWNE NARZĘDZIE**
**Profesjonalna aplikacja GUI** do tworzenia armii:
- 🎮 **Przyjazny interfejs** z suwakami i podglądem
- ⚙️ **Pełna kontrola** parametrów (5-25 żetonów, 250-1000 VP)
- 🧠 **Inteligentne balansowanie** armii
- 🎲 **Generator losowych** armii
- 💾 **W pełni automatyczne** tworzenie (bez dialogów!)
- 📊 **Progress bar** i monitoring

### `universal_army_creator.py`
Tworzy **predefiniowane** armie dla wszystkich 4 dowódców:
- Dowódca 2 (Polska) - Armia Górska
- Dowódca 3 (Polska) - Armia Kawalerii  
- Dowódca 5 (Niemcy) - Panzer Division
- Dowódca 6 (Niemcy) - Infantry Division

### `auto_token_creator.py`
Tworzy **tylko armię dowódcy 1** (5 żetonów, 125 VP)

### Dokumentacja
- `ARMY_CREATOR_STUDIO.md` - **pełna instrukcja GUI** ⭐
- `UNIWERSALNY_TWORCA_ARMII.md` - dokumentacja predefiniowanych armii
- `ARMIA_DOWODCY_1_AUTOMATYCZNA.md` - dokumentacja armii dowódcy 1

## Jak używać

### 🎖️ Army Creator Studio (ZALECANE):
```bash
python tools/army_automation/army_creator_studio.py
```
**➡️ Otwiera GUI aplikację z pełną kontrolą nad parametrami**

### 📋 Predefiniowane armie:
```bash  
python tools/army_automation/universal_army_creator.py
```
**➡️ Tworzy 4 gotowe armie bez wyboru parametrów**

### 🎯 Tylko dowódca 1:
```bash
python tools/army_automation/auto_token_creator.py
```
**➡️ Szybkie utworzenie podstawowej armii**

## Porównanie Narzędzi

| Narzędzie | GUI | Kontrola | Armie | VP Range | Żetony |
|-----------|-----|----------|-------|----------|---------|
| **Army Creator Studio** | ✅ | Pełna | Dowolne | 250-1000 | 5-25 |
| Universal Army Creator | ❌ | Brak | 4 predef. | ~710 | 18 |
| Auto Token Creator | ❌ | Brak | 1 predef. | 125 | 5 |

## Rezultat

Wszystkie narzędzia tworzą:
- **Kompletne żetony** (JSON + PNG)
- **Pełną strukturę katalogów** 
- **Historycznie poprawne nazwy**
- **Automatyczne aktualizowanie index.json**
- **Bez interakcji z użytkownikiem**

---

*Narzędzia stworzone dla projektu Kampania 1939*
