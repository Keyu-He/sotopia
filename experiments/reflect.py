"""
Play-Reflect-Transfer pipeline for self-improvement experiments.

Usage:
    python -m experiments.reflect \
        --log-pattern "logs/episode_reflect_baseline_werewolves_*.json" \
        --model gpt-5 \
        --output experiments/reflections/gpt5_werewolves.txt
"""

import argparse
import asyncio
import glob
import json
import os

from litellm import acompletion

from experiments.utils import load_game_config


def get_game_description(game_name: str) -> str:
    """Load game description from config.json."""
    config = load_game_config(game_name)
    return config.get("description", "")


def load_roster_roles(log_data: dict, roster_dir: str) -> dict[str, str]:
    """Load agent name -> role mapping from the roster file."""
    roster_file = log_data.get("metadata", {}).get("roster_file", "")
    if roster_file and roster_dir:
        roster_path = os.path.join(roster_dir, roster_file)
        if os.path.exists(roster_path):
            with open(roster_path) as f:
                roster = json.load(f)
            return {
                a["name"]: a.get("role", "Unknown") for a in roster.get("agents", [])
            }
    return {}


def format_game_summary(log_data: dict, game_idx: int, roster_dir: str = "") -> str:
    """Format a single game into a readable trajectory summary."""
    turns = log_data.get("turns", [])
    rewards = log_data.get("rewards", [])
    mm = log_data.get("model_mapping", {})
    agents = list(mm.keys())

    # Map agent names to roles from roster
    agent_roles = load_roster_roles(log_data, roster_dir)

    # Determine winners/losers
    r_vals = [float(r[0]) if isinstance(r, list) else float(r) for r in rewards]
    winners = [agents[i] for i in range(len(agents)) if r_vals[i] > 0]
    losers = [agents[i] for i in range(len(agents)) if r_vals[i] < 0]

    lines = [f"=== Game {game_idx + 1} ==="]
    lines.append(
        "Players: " + ", ".join(f"{a} ({agent_roles.get(a, '?')})" for a in agents)
    )
    lines.append(f"Winners: {', '.join(winners)}")
    lines.append(f"Losers: {', '.join(losers)}")
    lines.append("")

    for t in turns:
        name = t.get("agent_name", "")
        response = t.get("response", "")
        try:
            action = json.loads(response)
            action_str = action.get("argument", response)
        except (json.JSONDecodeError, TypeError):
            action_str = response[:200] if response else "(no response)"
        lines.append(f"  Turn {t['turn_number']:>2} [{name}]: {action_str}")

    lines.append("")
    return "\n".join(lines)


def build_reflection_prompt(
    game_description: str, game_summaries: str, num_games: int
) -> str:
    """Build the reflection prompt."""
    return f"""You just played {num_games} games of the following game (self-play — you controlled all players):

--- GAME DESCRIPTION ---
{game_description}
--- END GAME DESCRIPTION ---

Below are the full trajectories of all {num_games} games, showing every player's actions and the outcome:

{game_summaries}

Reflect on your play across all {num_games} games. Write an **internal monologue** of transferable social reasoning skills you learned. Frame your insights around general capabilities that apply across many social games, such as:

- **Deception**: hiding your true intentions, bluffing, maintaining a consistent false persona
- **Detection**: identifying when others are lying, spotting inconsistencies, reading behavioral patterns
- **Persuasion**: convincing others to act in your interest, building credibility, framing arguments
- **Information management**: when to reveal, withhold, or fabricate information; timing of disclosures
- **Coalition dynamics**: building alliances, breaking enemy alliances, knowing when to lead vs follow
- **Timing and patience**: when to act early vs wait, when to commit vs stay flexible

Requirements:
- Write in first person ("I should...", "When I need to hide information...", "A pattern I noticed is...")
- Derive insights from the games above, but write the rules so they apply beyond this specific game
- Focus on actionable lessons, not abstract observations
- Do NOT reference specific game numbers (e.g., "Game 3", "Games 5–8"). Your future self will not have access to these transcripts, so such references would be meaningless
- Keep it under 500 words

This monologue will be prepended to your system prompt in future social games (not just this one). Write it so that reading it once before any social strategy game will meaningfully improve your play.
"""


async def run_reflection(
    log_pattern: str, model: str, output_path: str, game: str, roster_dir: str = ""
) -> None:
    """Read game logs, format trajectories, prompt model for reflection."""
    log_files = sorted(glob.glob(log_pattern))
    if not log_files:
        print(f"No logs found matching: {log_pattern}")
        return

    print(f"Found {len(log_files)} game logs")

    # Load game description from config
    game_description = get_game_description(game)
    if not game_description:
        print(f"Warning: could not load description for game '{game}'")

    # Format all game summaries
    summaries = []
    for i, f in enumerate(log_files):
        data = json.load(open(f))
        summaries.append(format_game_summary(data, i, roster_dir=roster_dir))

    all_summaries = "\n".join(summaries)
    prompt = build_reflection_prompt(game_description, all_summaries, len(log_files))

    print(f"Prompt length: {len(prompt)} chars")
    print(f"Calling {model} for reflection...")

    # Build API call kwargs
    kwargs = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_completion_tokens": 4096,
    }

    if model.startswith("custom"):
        base_url = model.split("@")[1]
        api_key = os.environ.get("CUSTOM_API_KEY", "EMPTY")
        clean_model = model.split("@")[0].replace("custom/", "openai/")
        kwargs.update({"model": clean_model, "base_url": base_url, "api_key": api_key})
        del kwargs["max_completion_tokens"]
        kwargs["max_tokens"] = 4096

    response = await acompletion(**kwargs)
    reflection = response.choices[0].message.content

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(reflection)

    print(f"\nReflection saved to: {output_path}")
    print(f"Length: {len(reflection)} chars")
    print("\n--- Full Reflection ---")
    print(reflection)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Play-Reflect-Transfer Pipeline")
    parser.add_argument(
        "--log-pattern", required=True, help="Glob pattern for game logs"
    )
    parser.add_argument("--model", required=True, help="Model to use for reflection")
    parser.add_argument("--game", required=True, help="Game name (e.g. werewolves)")
    parser.add_argument(
        "--output", required=True, help="Output path for reflection text"
    )
    parser.add_argument(
        "--roster-dir", default="", help="Directory containing roster JSON files"
    )

    args = parser.parse_args()
    asyncio.run(
        run_reflection(
            args.log_pattern, args.model, args.output, args.game, args.roster_dir
        )
    )
