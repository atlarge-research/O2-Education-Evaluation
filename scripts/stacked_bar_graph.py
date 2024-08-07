import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import shared_config as sc
import seaborn as sns
import sys


def create_stacked_bar_graph(all_data=False):
    average_df = pd.read_csv(sc.average_output)
    if average_df.empty:
        print("Average CSV is empty!")
        exit()
    if "base" in sc.experiment_name:
        average_df.set_index("Chunks", inplace=True)
        x_label = "Circuits"
    elif "players" in sc.experiment_name:
        average_df.set_index("players", inplace=True)
        x_label = "Players"
    elif "gen" in sc.experiment_name or "pareto" in sc.experiment_name:
        average_df.set_index("terrain_type", inplace=True)
        x_label = "TerrainType"
    else:
        raise ValueError("Invalid experiment name")

    average_df.sort_index(inplace=True)

    final_columns = [
        "TerrainLogicSystem_other",
        "GetUpdates",
        "ReevaluatePropagateMarker",
        "PropagateLogicState",
        "CheckGateState",
    ]

    if "PropInputBlocks" in average_df.columns:
        final_columns.insert(len(final_columns) - 2, "PropInputBlocks")
        final_columns.insert(len(final_columns) - 2, "PropActiveLogicBlocks")
        final_columns.remove("PropagateLogicState")

    addition = 1
    legend = "lower right"
    if all_data:
        final_columns = [
            "Main Thread_other",
            "ServerFixedUpdate_other",
            "StatisticsSystem",
            "TerrainLogicSystem",
            "TerrainGeneration",
            "StructureGeneration",
            "PlayerTerrainGenCheck",
        ] 
        addition = 2
        legend = "lower left"

    final_columns = [col for col in final_columns if col in average_df.columns]
    average_df[final_columns] = average_df[final_columns] / 1e6

    # Plot the stacked bar chart
    ax = average_df[final_columns].plot(kind="barh", stacked=True, figsize=(10, 6))

    plt.ylabel(x_label)
    plt.xlabel("Average Frame Time (ms)")

    plt.ylim(bottom=0)
    plt.legend(loc=legend)

    plt.tight_layout()
    # plt.show()
    plt.savefig(
        f"{sc.plots_directory}{sc.experiment_name}-stacked-bar-{addition}.pdf",
        format="pdf",
    )
    print(
        f"Saved plot to {sc.plots_directory}{sc.experiment_name}-stacked-bar-{addition}.pdf"
    )


if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == "all":
            create_stacked_bar_graph(all_data=True)
        else:
            print("Invalid argument. Usage: python3 stacked_bar_graph.py [all]")
    else:
        create_stacked_bar_graph()
