"""
parser.py - Modul de citire si validare a puzzle-urilor murder mystery.
Citeste fisiere JSON si verifica ca au structura corecta.
"""
import json
import os


# campurile obligatorii dintr-un puzzle
REQUIRED_FIELDS = ["title", "description", "suspects", "weapons", "locations", "clues"]

# tipurile de indicii acceptate si campurile pe care le necesita
CLUE_TYPES = {
    "not_suspect_weapon": ["suspect", "weapon"],
    "not_suspect_location": ["suspect", "location"],
    "not_weapon_location": ["weapon", "location"],
    "suspect_location": ["suspect", "location"],
    "weapon_location": ["weapon", "location"],
}


def load_puzzle(filepath):
    """
    Citeste un fisier JSON si returneaza dictionarul puzzle-ului.
    Arunca exceptie daca fisierul nu exista sau nu e JSON valid.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Fisierul '{filepath}' nu exista.")

    with open(filepath, "r", encoding="utf-8") as f:
        try:
            puzzle = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Fisierul '{filepath}' nu contine JSON valid: {e}")

    return puzzle


def validate_puzzle(puzzle):
    """
    Verifica ca un puzzle are toate campurile necesare si ca indiciile
    refera suspecti/arme/locatii existente.
    Returneaza (True, None) daca e valid, sau (False, mesaj_eroare) daca nu.
    """
    # verificam campurile obligatorii
    for field in REQUIRED_FIELDS:
        if field not in puzzle:
            return False, f"Campul obligatoriu '{field}' lipseste din puzzle."

    # verificam ca listele nu sunt goale
    for field in ["suspects", "weapons", "locations"]:
        if not isinstance(puzzle[field], list) or len(puzzle[field]) == 0:
            return False, f"Campul '{field}' trebuie sa fie o lista nevida."

    # verificam ca clues e o lista
    if not isinstance(puzzle["clues"], list):
        return False, "Campul 'clues' trebuie sa fie o lista."

    if len(puzzle["clues"]) == 0:
        return False, "Puzzle-ul trebuie sa aiba cel putin un indiciu."

    suspects = set(puzzle["suspects"])
    weapons = set(puzzle["weapons"])
    locations = set(puzzle["locations"])

    # verificam fiecare indiciu
    for i, clue in enumerate(puzzle["clues"]):
        if "type" not in clue:
            return False, f"Indiciul #{i+1} nu are campul 'type'."

        clue_type = clue["type"]
        if clue_type not in CLUE_TYPES:
            return False, f"Indiciul #{i+1} are tipul necunoscut '{clue_type}'."

        # verificam ca indiciul are campurile necesare
        required_clue_fields = CLUE_TYPES[clue_type]
        for cf in required_clue_fields:
            if cf not in clue:
                return False, f"Indiciul #{i+1} (tip '{clue_type}') nu are campul '{cf}'."

            # verificam ca valorile exista in listele puzzle-ului
            if cf == "suspect" and clue[cf] not in suspects:
                return False, f"Indiciul #{i+1}: suspectul '{clue[cf]}' nu exista in lista de suspecti."
            elif cf == "weapon" and clue[cf] not in weapons:
                return False, f"Indiciul #{i+1}: arma '{clue[cf]}' nu exista in lista de arme."
            elif cf == "location" and clue[cf] not in locations:
                return False, f"Indiciul #{i+1}: locatia '{clue[cf]}' nu exista in lista de locatii."

    return True, None


def load_and_validate(filepath):
    """
    Incarca si valideaza un puzzle dintr-un fisier.
    Returneaza puzzle-ul daca e valid, sau arunca exceptie daca nu.
    """
    puzzle = load_puzzle(filepath)
    valid, error = validate_puzzle(puzzle)
    if not valid:
        raise ValueError(f"Puzzle invalid: {error}")
    return puzzle
