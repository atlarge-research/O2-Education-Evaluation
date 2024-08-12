import pandas as pd
import matplotlib.pyplot as plt
import shared_config as sc
import numpy as np
import os
import re


def sort_list2_by_list1(list1, list2):
    order_dict = {value: index for index, value in enumerate(list1)}

    def extract_key(item):
        search = re.search(r"players(.+)\/", item)
        if search:
            val = search.group(1)
            if "-activeLogic" in val:
                key_part = f"{val.replace('-activeLogic_', '').replace('Empty', 'Flat')} (Logic Active)"
            else:
                key_part = val.replace("_", "").replace('Empty', 'Flat')

        return order_dict.get(key_part, float("inf"))

    sorted_list2 = sorted(list2, key=extract_key)

    return sorted_list2

def create_fps_scatter():
    player_experiments = [
        f"{sc.data_directory}{x}/"
        for x in os.listdir(sc.data_directory)
        if "players" in x and not "Dummy" in x
    ]
    average_dfes = [exp + "averaged_output.csv" for exp in player_experiments]

    order = [
        "Dummy",
        "Flat",
        "Flat (Logic Active)",
        "2-Layer (Logic Active)",
        "RollingHills",
        "RollingHills (Logic Active)",
    ]
    markers = ["", "o", "s", "p", "*", "X", "D"]
    fig, ax = plt.subplots(figsize=(10, 6))

    handles = []
    labels = []
    min_ys = []
    max_ys = []
    average_dfes = sort_list2_by_list1(order, average_dfes)
    for average_df_file in average_dfes:
        if not os.path.exists(average_df_file):
            print(f"{average_df_file} does not exist")
            continue
        average_df = pd.read_csv(average_df_file)
        average_df.set_index("players", inplace=True)

        search = re.search(r"players(.+)\/", average_df_file)
        if search:
            val = search.group(1)
            if "-activeLogic" in val:
                labels.append(f"{val.replace('-activeLogic_', '').replace('Empty', 'Flat')} (Logic Active)")
            else:
                labels.append(val.replace("_", "").replace("Empty", "Flat"))
        else:
            raise ValueError("Invalid experiment name")

        fps = 1 / (average_df["Main Thread"] / 1e9)
        average_df["FPS"] = fps

        x = average_df.index
        y = average_df["FPS"]

        max_ys.append(y.max())
        min_ys.append(y.min())

        a, b = np.polyfit(x, y, 1)
        marker = markers[order.index(labels[-1])]
        scatter = ax.scatter(x, y, alpha=0.6, marker=marker)
        (line,) = ax.plot(x, a * x + b)

        handles.append((scatter, line))

    legend_handles = [h[0] for h in handles] + [h[1] for h in handles]
    fig.legend(legend_handles, labels, bbox_to_anchor=[0.12, 0.15], loc="lower left")

    ax.set_xlabel("Players")
    ax.set_ylabel("Server FPS")

    plt.ylim(bottom=0)

    plt.tight_layout()
    plt.savefig(f"{sc.plots_directory}players-fps-1.pdf", format="pdf")
    print(f"Saved plot to {sc.plots_directory}players-fps.pdf")


if __name__ == "__main__":
    create_fps_scatter()
