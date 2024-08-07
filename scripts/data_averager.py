import pandas as pd
import glob
import os
import shared_config as sc
import sys


def average_data(players=False):
    summed_df = pd.read_csv(sc.summed_output)
    if summed_df.empty:
        print("Summed CSV is empty!")
        exit()

    if "base" in sc.experiment_name:
        summed_df.set_index("Chunks", inplace=True)
        summed_df.sort_index(inplace=True)
    elif "players" in sc.experiment_name:
        summed_df.set_index("players", inplace=True)
        summed_df.sort_index(inplace=True)
    elif "gen" in sc.experiment_name or "pareto" in sc.experiment_name:
        summed_df.set_index("terrain_type", inplace=True)
        summed_df.sort_index(inplace=True)
    else:
        raise ValueError("Invalid experiment name")

    columns_to_average = [
        "Main Thread",
        "ServerFixedUpdate",
        "TerrainGeneration",
        "PlayerTerrainGenCheck",
        "StructureGeneration",
        "TerrainLogicSystem",
        "GetUpdates",
        "ReevaluatePropagateMarker",
        "PropagateLogicState",
        "CheckGateState",
        "StatisticsSystem",
    ]
    if "PropInputBlocks" in summed_df.columns:
        columns_to_average.append("PropInputBlocks")
    if "PropActiveLogicBlocks" in summed_df.columns:
        columns_to_average.append("PropActiveLogicBlocks")
    
    average_df = summed_df[columns_to_average].div(
        summed_df["original_row_count"], axis=0
    )
    
    average_df["FPS"] = 1 / (average_df["Main Thread"] / 1e9)

    average_df["filename"] = summed_df[
        "filename"
    ]  # [x.split("_")[1] + (" (Logic Active)" if "-activeLogic" in x else "") for x in summed_df["filename"]]
    if players:
        average_df["players"] = summed_df.index
        average_df["Chunks"] = summed_df["Chunks"]
    elif "base" in sc.experiment_name:
        average_df["Chunks"] = summed_df.index
    elif "gen" in sc.experiment_name or "pareto" in sc.experiment_name:
        average_df["terrain_type"] = summed_df.index
        average_df["Chunks"] = summed_df["Chunks"]
        average_df["players"] = summed_df["players"]
        average_df["active_logic"] = summed_df["active_logic"]


    average_df.set_index("filename", inplace=True)

    subsets = {
        "Main Thread": [
            "ServerFixedUpdate",
        ],
        "ServerFixedUpdate": [
            "TerrainGeneration",
            "PlayerTerrainGenCheck",
            "StructureGeneration",
            "TerrainLogicSystem",
            "StatisticsSystem",
        ],
        "TerrainLogicSystem": [
            "GetUpdates",
            "ReevaluatePropagateMarker",
            "PropagateLogicState",
            "CheckGateState",
        ],
    }

    for main_column, subset_columns in subsets.items():
        if main_column in average_df.columns and all(
            col in average_df.columns for col in subset_columns
        ):
            subset_sum = average_df[subset_columns].sum(axis=1)
            average_df[main_column + "_other"] = average_df[main_column] - subset_sum
        
    system_logs = []
    for experiment in os.listdir(sc.experiment_directory):
        if sc.experiment_name in experiment:
            system_logs.append(f"{sc.experiment_directory}{experiment}/system_logs/server.csv")

    averages = []
    for system_log in system_logs:
        table = pd.read_csv(system_log, sep=";")
        table = table.tail(120)
        averages.append(table["proc.cpu_percent"].mean())

    average_df["CPU"] = averages

    average_df.to_csv(sc.average_output, index=True)
    print("Averaged CSV created successfully!")


if __name__ == "__main__":
    if "players" in sc.experiment_name:
        average_data(True)
    else:
        average_data()
