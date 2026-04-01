"""
Generate experiment rosters with explicit model-to-team assignment.

Usage:
    # Self-play (all agents same model)
    python -m experiments.generate_experiment_rosters \
        --game werewolves --n 30 --roster-dir selfplay_gpt5 \
        --all-model gpt-5

    # Cross-model, fixed assignment
    python -m experiments.generate_experiment_rosters \
        --game werewolves --n 30 --roster-dir qwen32b_R_wolf_vs_gpt5 \
        --team Werewolves --model "custom/Qwen/Qwen3-32B@http://localhost:8002/v1" --reflection experiments/reflections/gpt5_werewolves.txt \
        --team Villagers --model gpt-5
"""

import argparse
import json
import os
import random
import sys
import glob

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from experiments.utils import load_roster_template

NAME_POOL = [
    "James",
    "Mary",
    "Robert",
    "Patricia",
    "John",
    "Jennifer",
    "Michael",
    "Linda",
    "David",
    "Elizabeth",
    "William",
    "Barbara",
    "Richard",
    "Susan",
    "Joseph",
    "Jessica",
    "Thomas",
    "Sarah",
    "Charles",
    "Karen",
    "Christopher",
    "Nancy",
    "Daniel",
    "Lisa",
    "Matthew",
    "Betty",
    "Anthony",
    "Margaret",
    "Mark",
    "Sandra",
    "Donald",
    "Ashley",
    "Steven",
    "Kimberly",
    "Paul",
    "Emily",
    "Andrew",
    "Donna",
    "Joshua",
    "Michelle",
    "Kenneth",
    "Dorothy",
    "Kevin",
    "Carol",
    "Brian",
    "Amanda",
    "George",
    "Melissa",
    "Edward",
    "Deborah",
    "Ronald",
    "Stephanie",
    "Timothy",
    "Rebecca",
    "Jason",
    "Sharon",
    "Jeffrey",
    "Laura",
    "Ryan",
    "Cynthia",
    "Jacob",
    "Kathleen",
    "Gary",
    "Amy",
    "Nicholas",
    "Shirley",
    "Eric",
    "Angela",
    "Jonathan",
    "Helen",
    "Stephen",
    "Anna",
    "Larry",
    "Brenda",
    "Justin",
    "Pamela",
    "Scott",
    "Nicole",
    "Brandon",
    "Emma",
]


def generate_experiment_rosters(
    game: str,
    n: int,
    roster_dir: str,
    team_configs: list[dict],
    all_model: str = "",
    seed: int = 42,
    overwrite: bool = False,
) -> None:
    """
    Generate N rosters with explicit model/reflection assignment per team.

    team_configs: list of {"team": str, "model": str, "reflection": str|None}
    all_model: if set, all agents use this model (ignores team_configs)
    """
    load_roster_template(game)  # validate game exists

    out_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "rosters", roster_dir, game)
    )
    os.makedirs(out_dir, exist_ok=True)

    # Count existing rosters to support extending
    existing = len(glob.glob(os.path.join(out_dir, "*.json")))
    if existing > 0 and not overwrite:
        print(
            f"  {existing} rosters already exist. Generating {max(0, n - existing)} more."
        )
        start = existing
    else:
        start = 0
        if overwrite and existing > 0:
            for f in glob.glob(os.path.join(out_dir, "*.json")):
                os.remove(f)
            print(f"  Removed {existing} existing rosters.")

    # Build team -> config lookup
    if all_model:
        team_lookup = {}  # all agents get same model
    else:
        team_lookup = {tc["team"]: tc for tc in team_configs}

    # Check reflection files exist
    for tc in team_configs:
        rf = tc.get("reflection", "")
        if rf:
            abs_rf = os.path.abspath(rf)
            if not os.path.exists(abs_rf):
                raise FileNotFoundError(f"Reflection file not found: {abs_rf}")

    count = 0
    for i in range(start, n):
        random.seed(seed + i)

        config = load_roster_template(game)
        agents = config["agents"]

        # Assign models and reflection
        has_reflection = False
        for agent in agents:
            if all_model:
                agent["agent_model"] = all_model
                agent["include_reflection"] = False
            else:
                team = agent.get("team", "")
                tc = team_lookup.get(team)
                if tc:
                    agent["agent_model"] = tc["model"]
                    if tc.get("reflection"):
                        agent["include_reflection"] = True
                        has_reflection = True
                    else:
                        agent["include_reflection"] = False
                else:
                    print(
                        f"  Warning: no config for team '{team}', skipping agent {agent.get('name')}"
                    )

        # Add reflection file path if any agent uses it
        if has_reflection:
            # Find the reflection file from team_configs
            for tc in team_configs:
                if tc.get("reflection"):
                    config["reflection_file"] = os.path.abspath(tc["reflection"])
                    break

        # Shuffle agents and assign names
        random.shuffle(agents)
        name_pool = NAME_POOL.copy()
        random.shuffle(name_pool)
        for idx, agent in enumerate(agents):
            agent["name"] = name_pool[idx]

        config["seed"] = seed + i

        filename = f"roster_{game}_{roster_dir}_ep{i}.json"
        filepath = os.path.join(out_dir, filename)
        with open(filepath, "w") as f:
            json.dump(config, f, indent=4)
        count += 1

    print(f"  Generated {count} rosters in {out_dir}")
    print(f"  Total: {len(glob.glob(os.path.join(out_dir, '*.json')))}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate experiment rosters with explicit model-to-team assignment.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--game", required=True, help="Game name (e.g., werewolves)")
    parser.add_argument(
        "--n", type=int, required=True, help="Number of rosters to generate"
    )
    parser.add_argument(
        "--roster-dir", required=True, help="Subdirectory under experiments/rosters/"
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed (default: 42)"
    )
    parser.add_argument(
        "--overwrite", action="store_true", help="Overwrite existing rosters"
    )

    # Self-play shortcut
    parser.add_argument(
        "--all-model",
        type=str,
        default="",
        help="All agents use this model (self-play)",
    )

    # Per-team config: repeatable --team/--model/--reflection groups
    parser.add_argument(
        "--team", action="append", default=[], help="Team name (repeatable)"
    )
    parser.add_argument(
        "--model",
        action="append",
        default=[],
        help="Model for the corresponding --team (repeatable)",
    )
    parser.add_argument(
        "--reflection",
        action="append",
        default=[],
        help="Reflection file for the corresponding --team (repeatable, use '' for none)",
    )

    args = parser.parse_args()

    # Build team configs from repeated args
    team_configs = []
    for i in range(len(args.team)):
        tc = {
            "team": args.team[i],
            "model": args.model[i] if i < len(args.model) else "",
        }
        if i < len(args.reflection) and args.reflection[i]:
            tc["reflection"] = args.reflection[i]
        team_configs.append(tc)

    if not args.all_model and not team_configs:
        parser.error("Must specify --all-model or at least one --team/--model pair")

    generate_experiment_rosters(
        game=args.game,
        n=args.n,
        roster_dir=args.roster_dir,
        team_configs=team_configs,
        all_model=args.all_model,
        seed=args.seed,
        overwrite=args.overwrite,
    )
