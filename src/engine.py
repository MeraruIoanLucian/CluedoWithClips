# engine.py
import os
import clips


# calea catre fisierul de reguli CLIPS
RULES_FILE = os.path.join(os.path.dirname(__file__), "..", "clips", "rules.clp")


def solve(puzzle, facts_list):
    env = clips.Environment()

    rules_path = os.path.abspath(RULES_FILE)
    if not os.path.exists(rules_path):
        raise FileNotFoundError(f"Fisierul de reguli CLIPS nu exista: {rules_path}")

    env.load(rules_path)

    for fact_str in facts_list:
        env.assert_string(fact_str)

    env.run()

    solution = None
    for fact in env.facts():
        if fact.template is not None and fact.template.name == "solution":
            solution = {
                "suspect": fact["suspect"],
                "weapon": fact["weapon"],
                "location": fact["location"]
            }
            break

    return solution


def get_remaining_possibilities(puzzle, facts_list):
    env = clips.Environment()
    rules_path = os.path.abspath(RULES_FILE)
    env.load(rules_path)

    for fact_str in facts_list:
        env.assert_string(fact_str)

    env.run()

    possibilities = []
    for fact in env.facts():
        if fact.template is not None and fact.template.name == "possible":
            possibilities.append({
                "suspect": fact["suspect"],
                "weapon": fact["weapon"],
                "location": fact["location"]
            })

    return possibilities
