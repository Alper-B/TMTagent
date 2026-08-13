import csv
import math
import random
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from analyze_tmt_log import TMTLogAnalyzer, DISTANCE_THRESHOLDS, CLICK_TIME_THRESHOLDS, plot_miss_surface
from enviromentTMT import TMTTaskProvider
from agent import CognitiveAgent

import numpy as np

OUTPUT_DIR = Path(__file__).resolve().parent / "simulation_results"
SIMULATION_SUMMARY_CSV = OUTPUT_DIR / "simulation_summary.csv"
SIMULATION_PLOTS_DIR = OUTPUT_DIR / "plots"

DEFAULT_PARAMS = {
    "search_speed": 150,
    "shift_speed": 50,
    "memory_speed": 150,
    "visual_capacity": 3,
    "visual_skip": 0,
    "click_overhead": 0,
    "mouse_speed": 0.4,
}


def run_simulation(task_type, params, seed=None):
    env = TMTTaskProvider(task_type=task_type, seed=seed)
    agent = CognitiveAgent(**params)

    total_time = 0.0
    click_times = []
    average_distance = 0.0

    for frame in agent.run_simulation(env):
        total_time += frame["time_cost"]

    target_count = len(env.targets)
    if target_count:
        average_click_time = total_time / target_count
    else:
        average_click_time = 0.0

    if len(agent.events) > 0:
        distances = []
        last_pos = None
        for event in agent.events:
            if event["event_type"] == "mouse_move":
                pos = (event["x"], event["y"])
                if last_pos is not None:
                    distances.append(math.hypot(pos[0] - last_pos[0], pos[1] - last_pos[1]))
                last_pos = pos
        if distances:
            average_distance = sum(distances) / len(distances)

    default_analyzer = TMTLogAnalyzer()
    default_summary = default_analyzer.analyze(agent.events)

    return {
        "task_type": task_type,
        "total_time_ms": round(total_time, 3),
        "average_click_time_ms": round(average_click_time, 3),
        "miss_count": default_summary["miss_count"],
        "average_mouse_distance": round(average_distance, 3),
        "params": params,
        "events": agent.events,
    }


def write_summary(rows):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(SIMULATION_SUMMARY_CSV, "w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "participant",
            "task_type",
            "total_time_ms",
            "average_click_time_ms",
            "miss_count",
            "average_mouse_distance",
            "search_speed",
            "shift_speed",
            "memory_speed",
            "visual_capacity",
            "visual_skip",
            "click_overhead",
            "mouse_speed",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            output_row = {
                "participant": row.get("participant", "unknown"),
                "task_type": row["task_type"],
                "total_time_ms": row["total_time_ms"],
                "average_click_time_ms": row["average_click_time_ms"],
                "miss_count": row["miss_count"],
                "average_mouse_distance": row["average_mouse_distance"],
                **row["params"],
            }
            writer.writerow(output_row)


def compute_simulation_miss_grid(events):
    grid = np.zeros((len(CLICK_TIME_THRESHOLDS), len(DISTANCE_THRESHOLDS)), dtype=int)
    for i_dist, dist in enumerate(DISTANCE_THRESHOLDS):
        for j_click, click_time in enumerate(CLICK_TIME_THRESHOLDS):
            analyzer = TMTLogAnalyzer(dist, click_time)
            summary = analyzer.analyze(events)
            grid[j_click, i_dist] = summary["miss_count"]
    return grid


def main():
    params = DEFAULT_PARAMS.copy()
    results = []

    for task_type in ["A", "B"]:
        for subject in ["subA", "subB", "subC"]:
            seed = random.randint(0, 10000)
            result = run_simulation(task_type, params, seed=seed)
            result["participant"] = subject
            results.append(result)

    write_summary(results)

    for row in results:
        event_grid = compute_simulation_miss_grid(row["events"])
        plot_path = SIMULATION_PLOTS_DIR / f"{row['participant']}_{row['task_type']}_miss_surface.png"
        output_path = plot_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plot_miss_surface(row["participant"], row["task_type"], DISTANCE_THRESHOLDS, CLICK_TIME_THRESHOLDS, event_grid, output_path)

    print(f"Simulation summary written to: {SIMULATION_SUMMARY_CSV}")
    print(f"Simulation plots written to: {SIMULATION_PLOTS_DIR}")
    for row in results:
        print(
            f"{row['participant']} TMT-{row['task_type']} -> total={row['total_time_ms']} ms, avg_click={row['average_click_time_ms']} ms, misses={row['miss_count']}"
        )


if __name__ == "__main__":
    main()
