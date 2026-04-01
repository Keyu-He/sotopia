import json
import glob
import os
import csv
import random
from collections import defaultdict
from typing import Any, Dict

from experiments.utils import load_game_config

# Simple ELO implementation
K_FACTOR = 32
STARTING_ELO = 1200
ELO_EPOCHS = 1

# Games where the optimal outcome requires cooperation / coordination.
# These are excluded from the main competitive ELO and shown separately.
COOPERATIVE_GAMES = {"battle_of_the_sexes", "stag_hunt", "public_goods", "centipede"}

# Canonical model name mapping: raw model string → display name.
# Handles endpoint changes, naming inconsistencies, etc.
MODEL_NAME_MAP = {
    # OpenAI
    "gpt-4o": "gpt-4o",
    "gpt-4o-mini": "gpt-4o-mini",
    "gpt-5": "gpt-5",
    # Qwen 3 32B (includes old qwen3.5-35b-a3b which was replaced)
    "qwen/qwen3-32b": "Qwen3-32B",
    "Qwen/Qwen3-32B": "Qwen3-32B",
    "qwen/qwen3.5-35b-a3b": "Qwen3-32B",
    # Qwen 3 4B
    "qwen/qwen3-4b-2507": "Qwen3-4B",
    "Qwen/Qwen3-4B-Instruct-2507": "Qwen3-4B",
    # Qwen 2.5 3B
    "qwen2.5-3b-instruct": "Qwen2.5-3B",
    "Qwen/Qwen2.5-3B-Instruct": "Qwen2.5-3B",
    # Gemma
    "google/gemma-3-27b": "Gemma3-27B",
    "google/gemma-3-27b-it": "Gemma3-27B",
}


def normalize_model_name(raw: str) -> str:
    """Normalize a raw model string to a canonical display name."""
    # Strip custom/ prefix and @url suffix
    name = raw.split("@")[0].replace("custom/", "")
    if name in MODEL_NAME_MAP:
        return MODEL_NAME_MAP[name]
    return name


def is_team_game(game_name: str) -> bool:
    """A team game has 2+ teams and >2 players."""
    config = load_game_config(game_name)
    agents = config.get("agents", [])
    teams = {a.get("team") for a in agents if a.get("team")}
    return len(teams) >= 2 and len(agents) > 2


def expected_score(rating_a: float, rating_b: float) -> float:
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))


def generate_single_table_html(
    title: str, stats: list[dict[str, Any]], show_split_elo: bool = True
) -> str:
    """Generates the HTML for a single leaderboard table."""
    rows_html = ""
    for item in stats:
        rank = item["rank"]
        rank_display = f"#{rank}"
        if rank == 1:
            rank_display = "🥇"
        if rank == 2:
            rank_display = "🥈"
        if rank == 3:
            rank_display = "🥉"

        name = item["model"]
        provider = "Unknown"
        # Heuristic for provider
        lower_name = name.lower()
        if "gpt" in lower_name:
            provider = "OpenAI"
        elif "qwen" in lower_name:
            provider = "Alibaba"
        elif "gemini" in lower_name or "google" in lower_name:
            provider = "Google"
        elif "claude" in lower_name:
            provider = "Anthropic"
        elif "llama" in lower_name:
            provider = "Meta"
        elif "mistral" in lower_name:
            provider = "Mistral"

        wr_val = item["win_rate"]
        wr_color = f"hsl({int(wr_val * 1.2)}, 70%, 40%)"

        split_elo_cells = ""
        if show_split_elo:
            split_elo_cells = f"""
            <td class="elo-split">{int(item['elo_w'])}</td>
            <td class="elo-split">{int(item['elo_v'])}</td>
            """
        else:
            split_elo_cells = """
            <td class="elo-split" style="color: #ccc;">-</td>
            <td class="elo-split" style="color: #ccc;">-</td>
            """

        row = f"""
        <tr>
            <td class="rank">{rank_display}</td>
            <td>
                <div class="model-cell">
                    <span class="model-name">{name}</span>
                    <span class="model-provider"><span class="provider-icon"></span> {provider}</span>
                </div>
            </td>
            <td class="elo">{int(item['elo'])}</td>
            {split_elo_cells}
            <td class="win-rate" style="color: {wr_color}">{item['win_rate']:.1f}%</td>
            <td class="matches">{item['matches']}</td>
        </tr>
        """
        rows_html += row

    split_headers = ""
    if show_split_elo:
        split_headers = """
                    <th>ELO-Alt (Wolf/Spy)</th>
                    <th>ELO-Main (Vil/Civ)</th>
        """
    else:
        split_headers = """
                    <th></th>
                    <th></th>
        """

    table_html = f"""
    <div class="leaderboard-section">
        <h2>{title}</h2>
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Model</th>
                    <th>ELO</th>
                    {split_headers}
                    <th>Win Rate</th>
                    <th style="text-align: right;">Matches</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """
    return table_html


def generate_cooperative_table_html(title: str, stats: list[dict[str, Any]]) -> str:
    """Generates a win-rate-only table for cooperative/coordination games."""
    rows_html = ""
    # Re-rank by win rate
    sorted_stats = sorted(stats, key=lambda x: x["win_rate"], reverse=True)
    for rank, item in enumerate(sorted_stats, 1):
        rank_display = f"#{rank}"
        if rank == 1:
            rank_display = "🥇"
        if rank == 2:
            rank_display = "🥈"
        if rank == 3:
            rank_display = "🥉"

        name = item["model"]
        provider = "Unknown"
        lower_name = name.lower()
        if "gpt" in lower_name:
            provider = "OpenAI"
        elif "qwen" in lower_name:
            provider = "Alibaba"
        elif "gemini" in lower_name or "google" in lower_name:
            provider = "Google"
        elif "claude" in lower_name:
            provider = "Anthropic"
        elif "llama" in lower_name:
            provider = "Meta"
        elif "mistral" in lower_name:
            provider = "Mistral"

        wr_val = item["win_rate"]
        wr_color = f"hsl({int(wr_val * 1.2)}, 70%, 40%)"

        rows_html += f"""
        <tr>
            <td class="rank">{rank_display}</td>
            <td>
                <div class="model-cell">
                    <span class="model-name">{name}</span>
                    <span class="model-provider"><span class="provider-icon"></span> {provider}</span>
                </div>
            </td>
            <td class="win-rate" style="color: {wr_color}">{wr_val:.1f}%</td>
            <td class="matches">{item['matches']}</td>
        </tr>
        """

    return f"""
    <div class="leaderboard-section">
        <h2>{title}</h2>
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Model</th>
                    <th>Win Rate</th>
                    <th style="text-align: right;">Matches</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """


def generate_html_report(
    competitive_tables: Dict[str, list[dict[str, Any]]],
    cooperative_tables: Dict[str, list[dict[str, Any]]],
) -> str:
    """
    Generates the full HTML report.
    competitive_tables / cooperative_tables: { "Title": stats_list, ... }
    """

    def render_competitive_section(
        tables: Dict[str, list[dict[str, Any]]], overall_key: str
    ) -> str:
        html = ""
        if overall_key in tables:
            html += generate_single_table_html(
                f"{overall_key} Leaderboard", tables[overall_key], show_split_elo=True
            )
        for title in sorted(t for t in tables if t != overall_key):
            # Convert title back to game_name (e.g. "Rock Paper Scissors" -> "rock_paper_scissors")
            game_name = title.lower().replace(" ", "_")
            html += generate_single_table_html(
                f"{title} Leaderboard",
                tables[title],
                show_split_elo=is_team_game(game_name),
            )
        return html

    def render_cooperative_section(
        tables: Dict[str, list[dict[str, Any]]], overall_key: str
    ) -> str:
        html = ""
        if overall_key in tables:
            html += generate_cooperative_table_html(
                f"{overall_key} Leaderboard", tables[overall_key]
            )
        for title in sorted(t for t in tables if t != overall_key):
            html += generate_cooperative_table_html(
                f"{title} Leaderboard", tables[title]
            )
        return html

    competitive_html = render_competitive_section(
        competitive_tables, "Competitive Overall"
    )
    cooperative_html = render_cooperative_section(
        cooperative_tables, "Cooperative Overall"
    )

    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Elo Leaderboard</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #ffffff; color: #333; margin: 0; padding: 40px; }}
            h1 {{ font-size: 28px; font-weight: 700; margin-bottom: 30px; display: flex; align-items: center; gap: 10px; border-bottom: 2px solid #eee; padding-bottom: 20px; }}
            h1::before {{ content: "🏆"; font-size: 32px; }}
            h2 {{ font-size: 20px; font-weight: 600; margin-top: 40px; margin-bottom: 15px; color: #444; }}
            h3 {{ font-size: 16px; font-weight: 600; color: #888; margin: 10px 0 5px; text-transform: uppercase; letter-spacing: 1px; border-left: 4px solid #ccc; padding-left: 10px; }}
            .section-divider {{ margin: 60px 0 30px; border-top: 2px dashed #eee; padding-top: 30px; }}
            table {{ width: 100%; border-collapse: collapse; min-width: 800px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #f0f0f0; border-radius: 8px; overflow: hidden; }}
            th {{ text-align: left; font-size: 12px; font-weight: 700; text-transform: uppercase; color: #666; padding: 12px 16px; background-color: #f9f9f9; border-bottom: 1px solid #eee; }}
            td {{ padding: 12px 16px; border-bottom: 1px solid #f5f5f5; vertical-align: middle; }}
            tr:last-child td {{ border-bottom: none; }}
            .rank {{ width: 60px; font-weight: 700; color: #555; font-size: 16px; }}
            .model-cell {{ display: flex; flex-direction: column; }}
            .model-name {{ font-weight: 700; font-size: 15px; color: #000; }}
            .model-provider {{ font-size: 11px; color: #888; display: flex; align-items: center; gap: 4px; margin-top: 2px; }}
            .elo {{ font-weight: 700; font-size: 15px; width: 80px; }}
            .elo-split {{ font-weight: 500; font-size: 14px; width: 100px; color: #666; }}
            .win-rate {{ font-weight: 700; font-size: 15px; width: 100px; }}
            .matches {{ font-weight: 500; font-size: 14px; width: 80px; text-align: right; color: #666; }}
            .footer {{ margin-top: 50px; font-size: 13px; color: #888; border-top: 1px solid #eee; padding-top: 20px; }}
            .provider-icon {{ width: 10px; height: 10px; border-radius: 50%; background-color: #ddd; display: inline-block; }}
            /* Rank Colors */
            tr:nth-child(1) .rank {{ color: #d4af37; }}
            tr:nth-child(2) .rank {{ color: #c0c0c0; }}
            tr:nth-child(3) .rank {{ color: #cd7f32; }}
        </style>
    </head>
    <body>
        <h1>Social Games Tournament Results</h1>

        <h3>⚔️ Competitive Games</h3>
        {competitive_html}

        <div class="section-divider">
            <h3>🤝 Cooperative / Coordination Games</h3>
            <p style="color:#888; font-size:13px; margin-bottom:20px;">
                These games test coordination ability rather than competitive skill.
                ELO here reflects how well a model navigates coordination under conflicting preferences.
            </p>
            {cooperative_html}
        </div>

        <div class="footer">
            <p><strong>Metrics Explanation:</strong></p>
            <ul>
                <li><strong>ELO:</strong> Rating computed from pairwise comparisons within each game category.</li>
                <li><strong>ELO-Alt:</strong> Rating as the minority/hidden role (Werewolf, Spy, Undercover).</li>
                <li><strong>ELO-Main:</strong> Rating as the majority role (Villager, Non-Spy, Civilian).</li>
                <li><strong>Win Rate:</strong> Fraction of pairwise comparisons won (~50% expected for equal competition).</li>
                <li>Cooperative games (Battle of the Sexes, Stag Hunt) are excluded from the competitive ELO.</li>
            </ul>
        </div>
    </body>
    </html>
    """
    return html_template


def process_logs(log_files: list[str]) -> list[dict[str, Any]]:
    """
    Process log files with all-pairs ELO updates.

    - Team games (metadata has *_model keys beyond model_a/model_b):
        only compare cross-team pairs; agents on the same team are not compared.
    - Individual games: compare all pairs of agents.
    - Self-play pairs (same model) are skipped.
    """
    elo_overall: dict[str, float] = defaultdict(lambda: STARTING_ELO)
    elo_alt: dict[str, float] = defaultdict(
        lambda: STARTING_ELO
    )  # minority/hidden role
    elo_main: dict[str, float] = defaultdict(lambda: STARTING_ELO)  # majority role

    wins: dict[str, int] = defaultdict(int)
    total_pairwise: dict[str, int] = defaultdict(int)
    episodes_played: dict[str, int] = defaultdict(int)

    for epoch in range(ELO_EPOCHS):
        shuffled = list(log_files)
        random.shuffle(shuffled)
        first_epoch = epoch == 0

        for filepath in shuffled:
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)

                raw_mapping = data.get("model_mapping", {})
                model_mapping = {
                    k: normalize_model_name(v) for k, v in raw_mapping.items()
                }
                rewards = data.get("rewards", [])
                metadata = data.get("metadata", {})

                if not model_mapping or not rewards:
                    continue

                parsed_rewards = []
                for r in rewards:
                    if isinstance(r, (list, tuple)):
                        parsed_rewards.append(float(r[0]))
                    else:
                        parsed_rewards.append(float(r))

                if len(model_mapping) != len(parsed_rewards):
                    continue

                agents = list(model_mapping.keys())
                agent_rewards = {
                    agents[i]: parsed_rewards[i] for i in range(len(agents))
                }

                if first_epoch:
                    for m in set(model_mapping.values()):
                        episodes_played[m] += 1

                # Detect team structure: any metadata key ending in "_model"
                # beyond the generic model_a / model_b entries
                team_model_keys = {
                    k: v
                    for k, v in metadata.items()
                    if k.endswith("_model") and k not in ("model_a", "model_b")
                }

                alt_agents: list[str] = []
                main_agents: list[str] = []
                is_team_game = False

                if len(team_model_keys) >= 2:
                    # Group agents by their team model
                    team_groups: dict[str, tuple[str, list[str]]] = {}
                    for team_key, team_model in team_model_keys.items():
                        team_name = team_key[: -len("_model")]
                        members = [
                            a for a, m in model_mapping.items() if m == team_model
                        ]
                        if members:
                            team_groups[team_name] = (team_model, members)

                    if len(team_groups) >= 2:
                        is_team_game = True
                        # Smaller team = alt (minority/hidden role); larger = main
                        sorted_teams = sorted(
                            team_groups.values(), key=lambda x: len(x[1])
                        )
                        _, alt_agents = sorted_teams[0]
                        _, main_agents = sorted_teams[-1]

                # Build pairs to compare
                if is_team_game:
                    # Cross-team only: every alt agent vs every main agent
                    pairs = [(a1, a2) for a1 in alt_agents for a2 in main_agents]
                else:
                    # All pairs
                    pairs = [
                        (agents[i], agents[j])
                        for i in range(len(agents))
                        for j in range(i + 1, len(agents))
                    ]

                for a1, a2 in pairs:
                    m1 = model_mapping[a1]
                    m2 = model_mapping[a2]

                    # Skip same-model self-play
                    if m1 == m2:
                        continue

                    r1 = agent_rewards[a1]
                    r2 = agent_rewards[a2]

                    if r1 > r2:
                        s1, s2 = 1.0, 0.0
                        if first_epoch:
                            wins[m1] += 1
                    elif r2 > r1:
                        s1, s2 = 0.0, 1.0
                        if first_epoch:
                            wins[m2] += 1
                    else:
                        s1, s2 = 0.5, 0.5

                    # Overall ELO
                    exp1 = expected_score(elo_overall[m1], elo_overall[m2])
                    exp2 = expected_score(elo_overall[m2], elo_overall[m1])
                    elo_overall[m1] += K_FACTOR * (s1 - exp1)
                    elo_overall[m2] += K_FACTOR * (s2 - exp2)

                    if first_epoch:
                        total_pairwise[m1] += 1
                        total_pairwise[m2] += 1

                    # Split ELO: alt role vs main role (team games only)
                    if is_team_game:
                        exp_alt = expected_score(elo_alt[m1], elo_main[m2])
                        exp_main = expected_score(elo_main[m2], elo_alt[m1])
                        elo_alt[m1] += K_FACTOR * (s1 - exp_alt)
                        elo_main[m2] += K_FACTOR * (s2 - exp_main)

            except Exception:
                continue

    # Build stats list
    sorted_models = sorted(
        elo_overall.keys(), key=lambda m: elo_overall[m], reverse=True
    )
    stats_list = []

    for rank, model in enumerate(sorted_models, 1):
        n_pairwise = total_pairwise[model]
        win_rate = (wins[model] / n_pairwise * 100) if n_pairwise > 0 else 0.0
        stats_list.append(
            {
                "rank": rank,
                "model": model,
                "elo": elo_overall[model],
                "elo_w": elo_alt[model],
                "elo_v": elo_main[model],
                "win_rate": win_rate,
                "matches": episodes_played[model],
            }
        )

    return stats_list


def save_to_csv(title: str, stats: list[dict[str, Any]]) -> None:
    """Saves the stats list to a CSV file."""
    # Sanitize title to filename
    safe_title = title.lower().replace(" ", "_").replace("/", "_")
    filename = os.path.join("experiments", f"elo_results_{safe_title}.csv")

    headers = [
        "Rank",
        "Model",
        "ELO",
        "ELO-Alt (Wolf/Spy)",
        "ELO-Main (Vil/Civ)",
        "Win Rate",
        "Matches",
    ]

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for item in stats:
            writer.writerow(
                [
                    item["rank"],
                    item["model"],
                    int(item["elo"]),
                    int(item["elo_w"]),
                    int(item["elo_v"]),
                    f"{item['win_rate']:.1f}%",
                    item["matches"],
                ]
            )
    print(f"Generated CSV: {filename}")


def calculate_elo(log_dir: str = "logs") -> None:
    print(f"Calculating ELO from logs in: {log_dir}")

    log_files = glob.glob(os.path.join(log_dir, "*.json"))
    print(f"Found {len(log_files)} items")

    # 1. Group logs by game, splitting competitive vs cooperative
    competitive_by_game: Dict[str, list[str]] = defaultdict(list)
    cooperative_by_game: Dict[str, list[str]] = defaultdict(list)

    for filepath in log_files:
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            metadata = data.get("metadata", {})
            game_name = metadata.get("game_name", "Unknown")
            bucket = (
                cooperative_by_game
                if game_name in COOPERATIVE_GAMES
                else competitive_by_game
            )
            bucket[game_name].append(filepath)
        except Exception:
            continue

    competitive_logs = [f for files in competitive_by_game.values() for f in files]
    cooperative_logs = [f for files in cooperative_by_game.values() for f in files]

    # 2. Competitive tables
    competitive_tables: Dict[str, list[dict[str, Any]]] = {}

    print("Processing Competitive Overall...")
    competitive_tables["Competitive Overall"] = process_logs(competitive_logs)
    save_to_csv("Competitive Overall", competitive_tables["Competitive Overall"])

    for game_name, game_logs in sorted(competitive_by_game.items()):
        if not game_name or game_name == "Unknown":
            continue
        print(f"Processing {game_name} ({len(game_logs)} games)...")
        title = game_name.replace("_", " ").title()
        stats = process_logs(game_logs)
        competitive_tables[title] = stats
        save_to_csv(title, stats)

    # 3. Cooperative tables
    cooperative_tables: Dict[str, list[dict[str, Any]]] = {}

    if cooperative_logs:
        print("Processing Cooperative Overall...")
        cooperative_tables["Cooperative Overall"] = process_logs(cooperative_logs)
        save_to_csv("Cooperative Overall", cooperative_tables["Cooperative Overall"])

        for game_name, game_logs in sorted(cooperative_by_game.items()):
            print(f"Processing {game_name} ({len(game_logs)} games)...")
            title = game_name.replace("_", " ").title()
            stats = process_logs(game_logs)
            cooperative_tables[title] = stats
            save_to_csv(title, stats)

    # 4. Generate HTML
    html_content = generate_html_report(competitive_tables, cooperative_tables)
    output_html = os.path.join("experiments", "elo_leaderboard.html")
    with open(output_html, "w") as f:
        f.write(html_content)

    print(f"\nSuccessfully generated {output_html}")
    all_titles = list(competitive_tables) + list(cooperative_tables)
    print("Tables generated for:", ", ".join(all_titles))


if __name__ == "__main__":
    calculate_elo()
