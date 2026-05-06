"""
converter.py - Modul de conversie puzzle JSON -> fapte CLIPS.
Transforma datele puzzle-ului in assertions compatibile cu motorul CLIPS.
"""


def puzzle_to_clips_facts(puzzle):
    """
    Converteste un puzzle (dict) intr-o lista de stringuri cu fapte CLIPS.
    Fiecare string e o comanda (assert ...) gata de executat.
    """
    facts = []

    # adaugam suspectii
    for suspect in puzzle["suspects"]:
        facts.append(f'(suspect (name "{suspect}"))')

    # adaugam armele
    for weapon in puzzle["weapons"]:
        facts.append(f'(weapon (name "{weapon}"))')

    # adaugam locatiile
    for location in puzzle["locations"]:
        facts.append(f'(location (name "{location}"))')

    # generam toate combinatiile posibile (suspect x arma x locatie)
    for suspect in puzzle["suspects"]:
        for weapon in puzzle["weapons"]:
            for location in puzzle["locations"]:
                facts.append(
                    f'(possible (suspect "{suspect}") '
                    f'(weapon "{weapon}") '
                    f'(location "{location}"))'
                )

    # convertim indiciile in fapte CLIPS
    for clue in puzzle["clues"]:
        clue_type = clue["type"]

        if clue_type == "not_suspect_weapon":
            facts.append(
                f'(clue-not-suspect-weapon (suspect "{clue["suspect"]}") '
                f'(weapon "{clue["weapon"]}"))'
            )
        elif clue_type == "not_suspect_location":
            facts.append(
                f'(clue-not-suspect-location (suspect "{clue["suspect"]}") '
                f'(location "{clue["location"]}"))'
            )
        elif clue_type == "not_weapon_location":
            facts.append(
                f'(clue-not-weapon-location (weapon "{clue["weapon"]}") '
                f'(location "{clue["location"]}"))'
            )
        elif clue_type == "suspect_location":
            facts.append(
                f'(clue-suspect-location (suspect "{clue["suspect"]}") '
                f'(location "{clue["location"]}"))'
            )
        elif clue_type == "weapon_location":
            facts.append(
                f'(clue-weapon-location (weapon "{clue["weapon"]}") '
                f'(location "{clue["location"]}"))'
            )

    return facts


def format_kb_display(puzzle):
    """
    Formateaza baza de cunostinte intr-un mod lizibil pentru afisare in CLI.
    Arata faptele CLIPS care vor fi incarcate.
    """
    facts = puzzle_to_clips_facts(puzzle)
    lines = []
    lines.append("=" * 50)
    lines.append("  BAZA DE CUNOSTINTE (Knowledge Base)")
    lines.append("=" * 50)
    lines.append("")

    lines.append("--- Suspecti ---")
    for f in facts:
        if f.startswith("(suspect"):
            lines.append(f"  {f}")
    lines.append("")

    lines.append("--- Arme ---")
    for f in facts:
        if f.startswith("(weapon"):
            lines.append(f"  {f}")
    lines.append("")

    lines.append("--- Locatii ---")
    for f in facts:
        if f.startswith("(location"):
            lines.append(f"  {f}")
    lines.append("")

    lines.append("--- Indicii (Reguli de eliminare) ---")
    for f in facts:
        if f.startswith("(clue"):
            lines.append(f"  {f}")
    lines.append("")
    lines.append("=" * 50)

    return "\n".join(lines)
