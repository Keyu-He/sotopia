import random
import os
import sys
import itertools
import json
import argparse
import glob

# Add project root to path to allow imports
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


def generate_rosters(
    game_names: list[str],
    models: list[str],
    individual_scenarios: int = 10,
    overwrite: bool = False,
    challenger: str | None = None,
    roster_dir: str = "",
) -> None:
    """
    Generate roster files for ELO tournament.

    Team-based games (2 distinct teams): pairwise matchups.
      team_episodes = max(1, ceil(individual_scenarios / num_pairs))
    Individual games (no teams / 1 team): random model per player slot, individual_scenarios total.
    """
    import math

    if not isinstance(game_names, list):
        game_names = [game_names]

    num_pairs = len(list(itertools.permutations(models, 2)))
    team_episodes = max(1, math.ceil(individual_scenarios / num_pairs))

    print(f"Generating rosters for games: {game_names}")
    print(f"Competitors: {models}")
    print(
        f"Team games: {num_pairs} pairs × {team_episodes} eps each (ceil({individual_scenarios}/{num_pairs}))"
    )
    print(f"Individual games: {individual_scenarios} random scenarios each")
    print("\n" + "=" * 50)

    for game_name in game_names:
        print(f"Processing game: {game_name}")

        try:
            template = load_roster_template(game_name)
        except Exception as e:
            print(f"  Error loading template for '{game_name}': {e}")
            continue

        if len(models) < 2:
            print(f"  Skipping {game_name}: Need at least 2 models.")
            continue

        roster_output_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "rosters", roster_dir, game_name)
            if roster_dir
            else os.path.join(os.path.dirname(__file__), "rosters", game_name)
        )
        os.makedirs(roster_output_dir, exist_ok=True)
        print(f"  Output directory: {roster_output_dir}")

        # Detect game type by checking for 2 distinct teams
        sample_agents = template["agents"]
        unique_teams = sorted({a.get("team") for a in sample_agents if a.get("team")})
        is_team_game = len(unique_teams) == 2

        count = 0

        if is_team_game:
            # --- TEAM GAME: pairwise, team_episodes per pair ---
            print(f"  Type: team-based ({unique_teams[0]} vs {unique_teams[1]})")
            for pair_idx, (model_a, model_b) in enumerate(
                itertools.permutations(models, 2)
            ):
                if challenger and challenger not in (model_a, model_b):
                    continue
                sanitized_m1 = model_a.split("@")[0].split("/")[-1]
                sanitized_m2 = model_b.split("@")[0].split("/")[-1]
                for i in range(team_episodes):
                    filename = f"roster_{game_name}_match{pair_idx}_ep{i}_{sanitized_m1}_vs_{sanitized_m2}.json"
                    file_path = os.path.join(roster_output_dir, filename)
                    semantic_suffix = f"ep{i}_{sanitized_m1}_vs_{sanitized_m2}.json"
                    if not overwrite and glob.glob(
                        os.path.join(roster_output_dir, f"*{semantic_suffix}")
                    ):
                        continue
                    if not overwrite and os.path.exists(file_path):
                        continue

                    try:
                        current_config = load_roster_template(game_name)
                    except Exception as e:
                        print(f"  Error loading template: {e}")
                        continue

                    agents = current_config["agents"]
                    t1, t2 = unique_teams[0], unique_teams[1]
                    for agent in agents:
                        if agent.get("team") == t1:
                            agent["agent_model"] = model_a
                        elif agent.get("team") == t2:
                            agent["agent_model"] = model_b
                        else:
                            agent["agent_model"] = model_a

                    random.shuffle(agents)
                    name_pool = NAME_POOL.copy()
                    random.shuffle(name_pool)
                    for idx, agent in enumerate(agents):
                        agent["name"] = name_pool[idx]

                    with open(file_path, "w") as f:
                        json.dump(current_config, f, indent=4)
                    count += 1

        else:
            # --- INDIVIDUAL GAME: random model per player slot ---
            print(f"  Type: individual ({len(sample_agents)} players)")
            for i in range(individual_scenarios):
                filename = f"roster_{game_name}_scenario{i}.json"
                file_path = os.path.join(roster_output_dir, filename)
                if not overwrite and os.path.exists(file_path):
                    continue

                try:
                    current_config = load_roster_template(game_name)
                except Exception as e:
                    print(f"  Error loading template: {e}")
                    continue

                agents = current_config["agents"]
                n_agents = len(agents)

                # Assign random model to each player slot (sample without replacement
                # if possible, else with replacement)
                if n_agents <= len(models):
                    assigned = random.sample(models, n_agents)
                else:
                    assigned = [random.choice(models) for _ in range(n_agents)]

                # Challenger filter: skip if challenger not in assigned models
                if challenger and challenger not in assigned:
                    continue

                for agent, model in zip(agents, assigned):
                    agent["agent_model"] = model

                random.shuffle(agents)
                name_pool = NAME_POOL.copy()
                random.shuffle(name_pool)
                for idx, agent in enumerate(agents):
                    agent["name"] = name_pool[idx]

                with open(file_path, "w") as f:
                    json.dump(current_config, f, indent=4)
                count += 1

        print(f"  Generated {count} NEW rosters for {game_name}")

    print("\nGeneration Complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Rosters for ELO Tournament")
    parser.add_argument(
        "--game",
        nargs="+",
        default=[
            "rock_paper_scissors",
            "battle_of_the_sexes",
            "chicken",
            "stag_hunt",
            "centipede",
            "prisoners_dilemma",
            "minority_game",
            "public_goods",
            "bargaining",
            "dead_last",
            "undercover",
            "spyfall",
            "chameleon",
            "insider",
            "liars_dice",
            "werewolves",
            "resistance",
            "coup",
            "survivor",
            "sheriff",
            "skull",
        ],
        help="List of games",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        default=[
            "gpt-4o-mini",
            "gpt-4o",
            "custom/qwen/qwen3.5-35b-a3b@http://127.0.0.1:1234/v1",
            "custom/google/gemma-3-27b@http://127.0.0.1:1234/v1",
            "custom/qwen/qwen3-4b-2507@http://127.0.0.1:1234/v1",
            "custom/qwen2.5-3b-instruct@http://127.0.0.1:1234/v1",
        ],
        help="List of models to compete",
    )
    parser.add_argument(
        "--individual-scenarios",
        type=int,
        default=5,
        help="Random scenarios for individual games; team episodes derived as ceil(this/num_pairs) (default: 5 for testing, use 30+ for full runs)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow generation even if output directory is not empty",
    )
    parser.add_argument(
        "--challenger",
        type=str,
        default=None,
        help="If set, only generate rosters involving this model",
    )
    parser.add_argument(
        "--roster-dir",
        type=str,
        default="v2",
        help="Subdirectory under experiments/rosters/ for this run (default: v2)",
    )

    args = parser.parse_args()

    generate_rosters(
        game_names=args.game,
        models=args.models,
        individual_scenarios=args.individual_scenarios,
        overwrite=args.overwrite,
        challenger=args.challenger,
        roster_dir=args.roster_dir,
    )
