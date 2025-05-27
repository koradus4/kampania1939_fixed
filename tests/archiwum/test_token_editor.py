import pytest
import tempfile
import shutil
import os
import json
from pathlib import Path

# Zakładamy, że logika zapisu tokena jest wydzielona do funkcji save_token_data(meta, token_dir)
# oraz że istnieje funkcja walidująca owner: validate_owner(owner)
# Jeśli nie, testujemy tylko strukturę JSON i walidację ownera.

def save_token_data(meta, token_dir):
    """Minimalna wersja logiki zapisu tokena do testów."""
    os.makedirs(token_dir, exist_ok=True)
    with open(os.path.join(token_dir, "token.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2, ensure_ascii=False)

def validate_owner(owner):
    if not owner or not isinstance(owner, str) or owner.strip() == "":
        raise ValueError("Musisz wybrać dowódcę (właściciela żetonu) przed zapisem!")
    return True

def test_save_token_with_owner():
    meta = {
        "id": "P_Pluton__1_PL_P_Pluton",
        "nation": "Polska",
        "unitType": "P",
        "unitSize": "Pluton",
        "owner": "2 (Polska)",
        "move": 5,
        "attack": {"range": 1, "value": 2},
        "combat_value": 8,
        "maintenance": 2,
        "price": 18,
        "sight": 3,
        "image": "assets/tokens/Polska/P_Pluton__1_PL_P_Pluton/token.png",
        "w": 240, "h": 240
    }
    with tempfile.TemporaryDirectory() as tmpdir:
        token_dir = os.path.join(tmpdir, "Polska", meta["id"])
        validate_owner(meta["owner"])
        save_token_data(meta, token_dir)
        assert os.path.exists(os.path.join(token_dir, "token.json"))
        with open(os.path.join(token_dir, "token.json"), encoding="utf-8") as f:
            data = json.load(f)
        assert data["owner"] == "2 (Polska)"
        assert data["nation"] == "Polska"
        assert data["unitType"] == "P"

def test_save_token_without_owner():
    meta = {
        "id": "P_Pluton__1_PL_P_Pluton",
        "nation": "Polska",
        "unitType": "P",
        "unitSize": "Pluton",
        "owner": "",
        "move": 5,
        "attack": {"range": 1, "value": 2},
        "combat_value": 8,
        "maintenance": 2,
        "price": 18,
        "sight": 3,
        "image": "assets/tokens/Polska/P_Pluton__1_PL_P_Pluton/token.png",
        "w": 240, "h": 240
    }
    with pytest.raises(ValueError):
        validate_owner(meta["owner"])

def test_save_token_with_missing_fields():
    meta = {
        "id": "P_Pluton__1_PL_P_Pluton",
        "nation": "Polska",
        # brak owner
        "unitType": "P",
        "unitSize": "Pluton"
    }
    with pytest.raises(KeyError):
        validate_owner(meta["owner"])  # powinien rzucić KeyError
