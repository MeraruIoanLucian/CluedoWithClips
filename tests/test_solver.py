"""
test_solver.py - Teste automate pentru Murder Mystery Puzzle Solver.
Testeaza parserul, convertorul, motorul CLIPS si cazurile limita.
"""
import sys
import os
import json
import tempfile

# adaugam src/ in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from parser import load_puzzle, validate_puzzle, load_and_validate
from converter import puzzle_to_clips_facts, format_kb_display
from engine import solve, get_remaining_possibilities


# directorul cu puzzle-uri
PUZZLES_DIR = os.path.join(os.path.dirname(__file__), "..", "puzzles")


def test_load_puzzle_valid():
    """Test: incarcarea unui puzzle JSON valid."""
    filepath = os.path.join(PUZZLES_DIR, "puzzle_01.json")
    puzzle = load_puzzle(filepath)
    assert "title" in puzzle
    assert "suspects" in puzzle
    assert "weapons" in puzzle
    assert "locations" in puzzle
    assert "clues" in puzzle
    print("  PASS - test_load_puzzle_valid")


def test_load_puzzle_file_not_found():
    """Test: fisier inexistent arunca FileNotFoundError."""
    try:
        load_puzzle("fisier_inexistent.json")
        assert False, "Ar fi trebuit sa arunce exceptie"
    except FileNotFoundError:
        print("  PASS - test_load_puzzle_file_not_found")


def test_load_puzzle_invalid_json():
    """Test: fisier cu JSON invalid arunca ValueError."""
    # cream un fisier temporar cu continut invalid
    tmp_path = os.path.join(os.path.dirname(__file__), "..", "puzzles", "_test_invalid.json")
    try:
        with open(tmp_path, "w") as f:
            f.write("{invalid json content!!!")
        try:
            load_puzzle(tmp_path)
            assert False, "Ar fi trebuit sa arunce exceptie"
        except ValueError:
            print("  PASS - test_load_puzzle_invalid_json")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_validate_puzzle_missing_field():
    """Test: puzzle cu camp lipsa returneaza eroare."""
    puzzle = {
        "title": "Test",
        "description": "Test",
        "suspects": ["A"],
        "weapons": ["W"],
        # lipseste "locations" si "clues"
    }
    valid, error = validate_puzzle(puzzle)
    assert not valid
    assert "locations" in error
    print("  PASS - test_validate_puzzle_missing_field")


def test_validate_puzzle_empty_suspects():
    """Test: lista de suspecti goala returneaza eroare."""
    puzzle = {
        "title": "Test",
        "description": "Test",
        "suspects": [],
        "weapons": ["W"],
        "locations": ["L"],
        "clues": [{"type": "not_suspect_weapon", "suspect": "A", "weapon": "W"}],
    }
    valid, error = validate_puzzle(puzzle)
    assert not valid
    assert "nevida" in error
    print("  PASS - test_validate_puzzle_empty_suspects")


def test_validate_puzzle_invalid_clue_type():
    """Test: indiciu cu tip necunoscut returneaza eroare."""
    puzzle = {
        "title": "Test",
        "description": "Test",
        "suspects": ["A", "B"],
        "weapons": ["W1", "W2"],
        "locations": ["L1", "L2"],
        "clues": [{"type": "tip_inexistent", "suspect": "A"}],
    }
    valid, error = validate_puzzle(puzzle)
    assert not valid
    assert "necunoscut" in error
    print("  PASS - test_validate_puzzle_invalid_clue_type")


def test_validate_puzzle_clue_wrong_suspect():
    """Test: indiciu care refera un suspect inexistent."""
    puzzle = {
        "title": "Test",
        "description": "Test",
        "suspects": ["Ana", "Bogdan"],
        "weapons": ["cutit", "pistol"],
        "locations": ["salon", "bucatarie"],
        "clues": [{"type": "not_suspect_weapon", "suspect": "Fantoma", "weapon": "cutit"}],
    }
    valid, error = validate_puzzle(puzzle)
    assert not valid
    assert "Fantoma" in error
    print("  PASS - test_validate_puzzle_clue_wrong_suspect")


def test_validate_puzzle_no_clues():
    """Test: puzzle fara indicii returneaza eroare."""
    puzzle = {
        "title": "Test",
        "description": "Test",
        "suspects": ["A", "B"],
        "weapons": ["W1", "W2"],
        "locations": ["L1", "L2"],
        "clues": [],
    }
    valid, error = validate_puzzle(puzzle)
    assert not valid
    assert "indiciu" in error
    print("  PASS - test_validate_puzzle_no_clues")


def test_converter_generates_facts():
    """Test: convertorul genereaza fapte CLIPS corecte."""
    puzzle = {
        "suspects": ["A", "B"],
        "weapons": ["W"],
        "locations": ["L"],
        "clues": [{"type": "not_suspect_weapon", "suspect": "B", "weapon": "W"}],
    }
    facts = puzzle_to_clips_facts(puzzle)
    # 2 suspecti + 1 arma + 1 locatie + 2 combinatii possible + 1 indiciu = 7
    assert len(facts) == 7
    assert any("suspect" in f and '"A"' in f for f in facts)
    assert any("possible" in f for f in facts)
    assert any("clue-not-suspect-weapon" in f for f in facts)
    print("  PASS - test_converter_generates_facts")


def test_converter_generates_all_combinations():
    """Test: convertorul genereaza toate combinatiile S x W x L."""
    puzzle = {
        "suspects": ["A", "B", "C"],
        "weapons": ["W1", "W2"],
        "locations": ["L1", "L2"],
        "clues": [],
    }
    facts = puzzle_to_clips_facts(puzzle)
    possible_facts = [f for f in facts if "possible" in f]
    # 3 suspecti x 2 arme x 2 locatii = 12
    assert len(possible_facts) == 12
    print("  PASS - test_converter_generates_all_combinations")


def test_format_kb_display():
    """Test: formatul KB arata sectiunile corecte."""
    puzzle = {
        "suspects": ["Ana"],
        "weapons": ["cutit"],
        "locations": ["salon"],
        "clues": [{"type": "not_suspect_weapon", "suspect": "Ana", "weapon": "cutit"}],
    }
    kb = format_kb_display(puzzle)
    assert "BAZA DE CUNOSTINTE" in kb
    assert "Suspecti" in kb
    assert "Arme" in kb
    assert "Locatii" in kb
    assert "Indicii" in kb
    print("  PASS - test_format_kb_display")


def test_solve_simple_puzzle():
    """Test: rezolvarea unui puzzle simplu cu 2 suspecti."""
    puzzle = {
        "suspects": ["Ana", "Bogdan"],
        "weapons": ["cutit"],
        "locations": ["salon"],
        "clues": [{"type": "not_suspect_weapon", "suspect": "Ana", "weapon": "cutit"}],
    }
    facts = puzzle_to_clips_facts(puzzle)
    solution = solve(puzzle, facts)
    assert solution is not None
    assert solution["suspect"] == "Bogdan"
    assert solution["weapon"] == "cutit"
    assert solution["location"] == "salon"
    print("  PASS - test_solve_simple_puzzle")


def test_solve_all_puzzles():
    """Test: toate puzzle-urile din directorul puzzles/ se rezolva corect."""
    import glob
    files = sorted(glob.glob(os.path.join(PUZZLES_DIR, "puzzle_*.json")))
    assert len(files) >= 5, f"Ar trebui sa fie cel putin 5 puzzle-uri, dar sunt {len(files)}"

    for filepath in files:
        puzzle = load_and_validate(filepath)
        facts = puzzle_to_clips_facts(puzzle)
        solution = solve(puzzle, facts)
        expected = puzzle.get("solution")

        filename = os.path.basename(filepath)
        assert solution is not None, f"{filename}: nu s-a gasit solutie"
        assert expected is not None, f"{filename}: lipseste solutia asteptata"
        assert solution["suspect"] == expected["suspect"], \
            f"{filename}: suspect gresit {solution['suspect']} != {expected['suspect']}"
        assert solution["weapon"] == expected["weapon"], \
            f"{filename}: arma gresita {solution['weapon']} != {expected['weapon']}"
        assert solution["location"] == expected["location"], \
            f"{filename}: locatie gresita {solution['location']} != {expected['location']}"

    print(f"  PASS - test_solve_all_puzzles ({len(files)} puzzle-uri)")


def test_solve_contradictory_puzzle():
    """Test: puzzle cu indicii contradictorii returneaza None."""
    puzzle = {
        "suspects": ["Ana"],
        "weapons": ["cutit"],
        "locations": ["salon"],
        "clues": [
            {"type": "not_suspect_weapon", "suspect": "Ana", "weapon": "cutit"},
        ],
    }
    facts = puzzle_to_clips_facts(puzzle)
    solution = solve(puzzle, facts)
    # Ana e singurul suspect dar nu poate folosi cutitul = contradictie
    assert solution is None
    print("  PASS - test_solve_contradictory_puzzle")


def test_solve_multiple_solutions():
    """Test: puzzle cu solutii multiple nu returneaza solutie unica."""
    puzzle = {
        "suspects": ["Ana", "Bogdan"],
        "weapons": ["cutit", "pistol"],
        "locations": ["salon"],
        "clues": [],  # niciun indiciu = 2 solutii posibile
    }
    facts = puzzle_to_clips_facts(puzzle)
    solution = solve(puzzle, facts)
    # cu 2 suspecti si 2 arme, fara indicii, nu poate fi o solutie unica
    assert solution is None
    print("  PASS - test_solve_multiple_solutions")


def test_remaining_possibilities():
    """Test: get_remaining_possibilities returneaza combinatiile ramase."""
    puzzle = {
        "suspects": ["Ana", "Bogdan"],
        "weapons": ["cutit"],
        "locations": ["salon"],
        "clues": [],
    }
    facts = puzzle_to_clips_facts(puzzle)
    remaining = get_remaining_possibilities(puzzle, facts)
    # 2 suspecti x 1 arma x 1 locatie = 2 combinatii
    assert len(remaining) == 2
    print("  PASS - test_remaining_possibilities")


def run_all_tests():
    """Ruleaza toate testele."""
    print("=" * 50)
    print("  TESTE AUTOMATE - Murder Mystery Puzzle Solver")
    print("=" * 50)
    print()

    tests = [
        # Parser tests
        ("Parser", [
            test_load_puzzle_valid,
            test_load_puzzle_file_not_found,
            test_load_puzzle_invalid_json,
            test_validate_puzzle_missing_field,
            test_validate_puzzle_empty_suspects,
            test_validate_puzzle_invalid_clue_type,
            test_validate_puzzle_clue_wrong_suspect,
            test_validate_puzzle_no_clues,
        ]),
        # Converter tests
        ("Converter", [
            test_converter_generates_facts,
            test_converter_generates_all_combinations,
            test_format_kb_display,
        ]),
        # Engine tests
        ("Engine (CLIPS)", [
            test_solve_simple_puzzle,
            test_solve_all_puzzles,
            test_solve_contradictory_puzzle,
            test_solve_multiple_solutions,
            test_remaining_possibilities,
        ]),
    ]

    total = 0
    passed = 0
    failed = 0

    for category, test_funcs in tests:
        print(f"--- {category} ---")
        for test_func in test_funcs:
            total += 1
            try:
                test_func()
                passed += 1
            except Exception as e:
                failed += 1
                print(f"  FAIL - {test_func.__name__}: {e}")
        print()

    print("=" * 50)
    print(f"  REZULTAT: {passed}/{total} teste trecute", end="")
    if failed > 0:
        print(f" ({failed} esuate)")
    else:
        print(" - TOATE TRECUTE!")
    print("=" * 50)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
