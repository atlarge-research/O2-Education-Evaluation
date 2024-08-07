import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import shared_config as sc
import seaborn as sns
import numpy as np
import os
import re


def create_line_graph():
    player_experiments = [
        f"{sc.data_directory}{x}/"
        for x in os.listdir(sc.data_directory)
        if "players" in x
    ]
    average_dfes = [exp + "averaged_output.csv" for exp in player_experiments]

    fig, ax = plt.subplots(1, 1, sharex=True, height_ratios=[10], figsize=(10, 6))

    handles = []
    labels = []
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
                val = f"{val.replace('-activeLogic_', '')} (Logic Active)"
            else:
                val = val.replace("_", "")
        else:
            raise ValueError("Invalid experiment name")

        x = average_df.index
        columns = [
            "StatisticsSystem",
            "PlayerTerrainGenCheck",
            "TerrainGeneration",
            "StructureGeneration",
            "TerrainLogicSystem",
        ]
        y = average_df[columns].sum(axis=1) / 1e6
        ax.plot(x, y, label=val)

    fig.legend(bbox_to_anchor=[0.06, 0.95], loc="upper left")

    fig.text(0.5, 0, "Players", ha="center")
    fig.text(0, 0.5, "Average frame time (ms)", va="center", rotation="vertical")

    plt.ylim(bottom=0)

    plt.tight_layout()
    # plt.show()
    plt.savefig(f"{sc.plots_directory}players-line-4.pdf", format="pdf")
    print(f"Saved plot to {sc.plots_directory}players-line-_.pdf")


if __name__ == "__main__":
    create_line_graph()
