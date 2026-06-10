# main.py
# Meniu interactiv pentru puzzle-uri
import os
import sys
import json
import glob

# path pentru import
sys.path.insert(0, os.path.dirname(__file__))

from parser import load_and_validate, validate_puzzle
from converter import puzzle_to_clips_facts, format_kb_display
from engine import solve

# directorul cu puzzle-uri
PUZZLES_DIR = os.path.join(os.path.dirname(__file__), "..", "puzzles")


def clear_screen():
    # curatam ecranul
    os.system("cls" if os.name == "nt" else "clear")


def print_header():
    print("\n--- MURDER MYSTERY PUZZLE SOLVER ---")
    print("Sistem Expert bazat pe CLIPS\n")


def print_menu():
    print("1. Listeaza puzzle-urile")
    print("2. Selecteaza un puzzle")
    print("3. Vizualizeaza date")
    print("4. Vizualizeaza KB")
    print("5. Rezolva")
    print("6. Adauga puzzle")
    print("0. Iesire\n")


def get_puzzle_files():
    # ia fisierele json
    pattern = os.path.join(os.path.abspath(PUZZLES_DIR), "*.json")
    files = sorted(glob.glob(pattern))
    return files


def list_puzzles():
    files = get_puzzle_files()
    if not files:
        print("  [!] Nu exista puzzle-uri in directorul 'puzzles/'.")
        return

    print("-" * 40)
    print("  PUZZLE-URI DISPONIBILE")
    print("-" * 40)
    for i, filepath in enumerate(files, 1):
        filename = os.path.basename(filepath)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            title = data.get("title", "Fara titlu")
            print(f"  {i}. {title} ({filename})")
        except Exception:
            print(f"  {i}. [eroare citire] ({filename})")
    print()


def select_puzzle(current_puzzle):
    files = get_puzzle_files()
    if not files:
        print("  [!] Nu exista puzzle-uri disponibile.")
        return current_puzzle

    list_puzzles()
    try:
        choice = input("  Numarul puzzle-ului: ").strip()
        idx = int(choice) - 1
        if idx < 0 or idx >= len(files):
            print("  [!] Numar invalid.")
            return current_puzzle
    except ValueError:
        print("  [!] Introduceti un numar valid.")
        return current_puzzle

    filepath = files[idx]
    try:
        puzzle = load_and_validate(filepath)
        print(f"\n  [OK] Puzzle selectat: {puzzle['title']}")
        print(f"       {puzzle['description']}")
        print(f"       Suspecti: {len(puzzle['suspects'])}, "
              f"Arme: {len(puzzle['weapons'])}, "
              f"Locatii: {len(puzzle['locations'])}")
        print(f"       Indicii: {len(puzzle['clues'])}")
        return puzzle
    except Exception as e:
        print(f"  [!] Eroare la incarcarea puzzle-ului: {e}")
        return current_puzzle


def view_puzzle_data(puzzle):
    if puzzle is None:
        print("  [!] Selecteaza mai intai un puzzle (optiunea 2).")
        return

    print()
    print("=" * 50)
    print(f"  {puzzle['title']}")
    print("=" * 50)
    print(f"\n  {puzzle['description']}\n")

    print("  SUSPECTI:")
    for s in puzzle["suspects"]:
        print(f"    - {s}")

    print("\n  ARME:")
    for w in puzzle["weapons"]:
        print(f"    - {w}")

    print("\n  LOCATII:")
    for l in puzzle["locations"]:
        print(f"    - {l}")

    print("\n  INDICII:")
    for i, clue in enumerate(puzzle["clues"], 1):
        clue_text = format_clue(clue)
        print(f"    {i}. {clue_text}")
    print()


def format_clue(clue):
    t = clue["type"]
    if t == "not_suspect_weapon":
        return f"{clue['suspect']} NU a folosit {clue['weapon']}"
    elif t == "not_suspect_location":
        return f"{clue['suspect']} NU era in {clue['location']}"
    elif t == "not_weapon_location":
        return f"{clue['weapon']} NU era in {clue['location']}"
    elif t == "suspect_location":
        return f"{clue['suspect']} ERA in {clue['location']}"
    elif t == "weapon_location":
        return f"{clue['weapon']} ERA in {clue['location']}"
    return str(clue)


def view_kb(puzzle):
    if puzzle is None:
        print("  [!] Selecteaza mai intai un puzzle (optiunea 2).")
        return

    kb_text = format_kb_display(puzzle)
    print()
    print(kb_text)
    print()


def solve_puzzle(puzzle):
    if puzzle is None:
        print("  [!] Selecteaza mai intai un puzzle (optiunea 2).")
        return

    print(f"\n  Rezolvare '{puzzle['title']}'...")
    print("  Se incarca faptele in motorul CLIPS...")

    facts = puzzle_to_clips_facts(puzzle)
    print(f"  {len(facts)} fapte incarcate.")
    print("  Se ruleaza motorul de inferenta...\n")

    try:
        solution = solve(puzzle, facts)
    except Exception as e:
        print(f"  [!] Eroare la rularea CLIPS: {e}")
        return

    if solution is None:
        print("  " + "=" * 44)
        print("  EROARE: Nu s-a gasit nicio solutie!")
        print("  Indiciile sunt contradictorii sau insuficiente.")
        print("  " + "=" * 44)
    else:
        print("  " + "=" * 44)
        print("  SOLUTIE GASITA!")
        print("  " + "=" * 44)
        print(f"  Criminal:  {solution['suspect']}")
        print(f"  Arma:      {solution['weapon']}")
        print(f"  Locatia:   {solution['location']}")
        print("  " + "=" * 44)

        # verificam cu solutia din puzzle daca exista
        if "solution" in puzzle:
            expected = puzzle["solution"]
            if (solution["suspect"] == expected["suspect"] and
                    solution["weapon"] == expected["weapon"] and
                    solution["location"] == expected["location"]):
                print("  [Verificare] Solutia este CORECTA!")
            else:
                print("  [Verificare] ATENTIE: Solutia difera de cea asteptata!")
    print()


def add_puzzle():
    print("\n--- ADAUGARE PUZZLE ---\n")

    title = input("  Titlul puzzle-ului: ").strip()
    if not title:
        print("  [!] Titlul nu poate fi gol.")
        return

    description = input("  Descrierea: ").strip()

    # suspecti
    print("  Introdu suspectii (cate unul pe linie, linie goala = gata):")
    suspects = []
    while True:
        s = input("    Suspect: ").strip()
        if not s:
            break
        suspects.append(s)
    if len(suspects) < 2:
        print("  [!] Trebuie cel putin 2 suspecti.")
        return

    # arme
    print("  Introdu armele (cate una pe linie, linie goala = gata):")
    weapons = []
    while True:
        w = input("    Arma: ").strip()
        if not w:
            break
        weapons.append(w)
    if len(weapons) < 2:
        print("  [!] Trebuie cel putin 2 arme.")
        return

    # locatii
    print("  Introdu locatiile (cate una pe linie, linie goala = gata):")
    locations = []
    while True:
        l = input("    Locatie: ").strip()
        if not l:
            break
        locations.append(l)
    if len(locations) < 2:
        print("  [!] Trebuie cel putin 2 locatii.")
        return

    # indicii
    print("\n  Introdu indiciile:")
    print("  Tipuri disponibile:")
    print("    1. not_suspect_weapon  - Suspectul X NU a folosit arma Y")
    print("    2. not_suspect_location - Suspectul X NU era in locatia Y")
    print("    3. not_weapon_location - Arma Y NU era in locatia Z")
    print("    4. suspect_location    - Suspectul X ERA in locatia Y")
    print("    5. weapon_location     - Arma Y ERA in locatia Z")
    print("  (linie goala = gata)\n")

    clue_types_map = {
        "1": "not_suspect_weapon",
        "2": "not_suspect_location",
        "3": "not_weapon_location",
        "4": "suspect_location",
        "5": "weapon_location",
    }

    clues = []
    while True:
        ct = input("  Tipul indiciului (1-5 sau gol): ").strip()
        if not ct:
            break
        if ct not in clue_types_map:
            print("  [!] Tip invalid.")
            continue

        clue_type = clue_types_map[ct]
        clue = {"type": clue_type}

        if "suspect" in clue_type:
            clue["suspect"] = input(f"    Suspect ({', '.join(suspects)}): ").strip()
        if "weapon" in clue_type:
            clue["weapon"] = input(f"    Arma ({', '.join(weapons)}): ").strip()
        if "location" in clue_type.replace("suspect_", "").replace("weapon_", ""):
            clue["location"] = input(f"    Locatie ({', '.join(locations)}): ").strip()

        clues.append(clue)
        print(f"  [+] Indiciu adaugat: {format_clue(clue)}")

    if len(clues) == 0:
        print("  [!] Trebuie cel putin un indiciu.")
        return

    # construim puzzle-ul
    puzzle = {
        "title": title,
        "description": description,
        "suspects": suspects,
        "weapons": weapons,
        "locations": locations,
        "clues": clues,
    }

    # validam
    valid, error = validate_puzzle(puzzle)
    if not valid:
        print(f"  [!] Puzzle invalid: {error}")
        return

    # salvam
    existing = get_puzzle_files()
    num = len(existing) + 1
    filename = f"puzzle_{num:02d}.json"
    filepath = os.path.join(os.path.abspath(PUZZLES_DIR), filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(puzzle, f, indent=2, ensure_ascii=False)

    print(f"\n  [OK] Puzzle salvat ca '{filename}'.")


def main():
    current_puzzle = None

    clear_screen()
    print_header()

    while True:
        print_menu()
        choice = input("  Optiunea ta: ").strip()

        if choice == "1":
            list_puzzles()
        elif choice == "2":
            current_puzzle = select_puzzle(current_puzzle)
        elif choice == "3":
            view_puzzle_data(current_puzzle)
        elif choice == "4":
            view_kb(current_puzzle)
        elif choice == "5":
            solve_puzzle(current_puzzle)
        elif choice == "6":
            add_puzzle()
        elif choice == "0":
            print("\n  La revedere!\n")
            break
        else:
            print("  [!] Optiune invalida. Incearca din nou.\n")


if __name__ == "__main__":
    main()
