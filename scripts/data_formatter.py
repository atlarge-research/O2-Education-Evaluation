import os
import re
import pandas as pd
import shared_config as sc

def run_formatter():
    experiments = os.listdir(sc.experiment_directory)
    experiments = [experiment for experiment in experiments if sc.experiment_name.split("_")[0] in experiment]

    server_stats = [f"{sc.experiment_directory}{experiment}/opencraft_stats/server.csv" for experiment in experiments]
    system_logs = [f"{sc.experiment_directory}{experiment}/system_logs/server.csv" for experiment in experiments]
    logic_active = ["-activeLogic" in name for name in experiments]
    terrain = [name.split("_")[1] for name in experiments]
    players = [re.search(r"(\d+)p", name).group(1) for name in experiments]
    time = [re.search(r"(\d+)s", name).group(1) for name in experiments]

    terrain_areas_header = "Number of Terrain Areas (Server)"
    num_player_header = "Number of Players (Server)"


    for i, server_stat in enumerate(server_stats):
        print(experiments[i], logic_active[i], terrain[i], players[i], time[i])
        output_file = f"{sc.formatted_stats_directory}{experiments[i]}.csv"
        table = pd.read_csv(server_stat, sep=";")
        table.drop(table.columns[len(table.columns)-1], axis=1, inplace=True)
        filtered_df = table
        
        if sc.filter_by_max_players:
            max_players = filtered_df[num_player_header].max()
            filtered_df = filtered_df[filtered_df[num_player_header] == max_players]
        if sc.filter_by_max_terrainarea:
            max_terrain = filtered_df[terrain_areas_header].max()
            filtered_df = filtered_df[filtered_df[terrain_areas_header] == max_terrain]
            if logic_active[i]:
                max_circuits = filtered_df["NumInputTypeBlocks"].max()
                filtered_df = filtered_df[filtered_df["NumInputTypeBlocks"] == max_circuits]
                filtered_df = filtered_df.iloc[1:]
        
        filtered_df.to_csv(output_file, index=False)
        

if __name__ == "__main__":
    run_formatter()