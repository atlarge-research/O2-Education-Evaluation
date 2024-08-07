import pandas as pd
import matplotlib.pyplot as plt
import shared_config as sc
import sys


def create_stacked_line_graph(all_data=False):
    average_df = pd.read_csv(sc.average_output)
    if average_df.empty:
        print("Average CSV is empty!")
        exit()
    if "base" in sc.experiment_name: 
        average_df.set_index("Chunks", inplace=True)
        x_label = "Circuits"
    elif  "players" in sc.experiment_name:
        average_df.set_index("players", inplace=True)
        x_label = "Players"
    elif "gen" in sc.experiment_name or "pareto" in sc.experiment_name:
        average_df.set_index("terrain_type", inplace=True)
        x_label = "Terrain Type"
    else:
        raise ValueError("Invalid experiment name")

    final_columns = [
        # "Main Thread_other",
        # "ServerFixedUpdate_other",
        "StatisticsSystem",
        "PlayerTerrainGenCheck",
        "TerrainGeneration",
        "StructureGeneration",
        "TerrainLogicSystem",
        # "GetUpdates",
        # "ReevaluatePropagateMarker",
        # "PropagateLogicState",
        # "CheckGateState", 
        # "Main Thread"   
    ]
    
    addition=1
    legend = "lower right"
    if all_data:
        final_columns = [
            "Main Thread_other",
            "ServerFixedUpdate_other",
        ] + final_columns
        addition = 2
        legend = "lower right"
    
    final_columns = [col for col in final_columns if col in average_df.columns]
    average_df[final_columns] = average_df[final_columns] / 1e6

    ax = average_df[final_columns].plot(kind='area', stacked=True, figsize=(10, 6), alpha=0.6)

    plt.xlabel(x_label)
    plt.ylabel('Average Frame Time (ms)')


    plt.ylim(bottom=0)
    plt.legend(loc=legend)

    plt.tight_layout()
    # plt.show()
    plt.savefig(f"{sc.plots_directory}{sc.experiment_name}-stacked-line-{addition}.pdf", format='pdf', bbox_inches="tight")
    print(f"Saved plot to {sc.plots_directory}{sc.experiment_name}-stacked-line-{addition}.pdf")
    
    
if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == "all":
            create_stacked_line_graph(True)
        else:
            print("Invalid argument. Usage: python3 stacked_line_graph.py [all]")
    else:
        create_stacked_line_graph()