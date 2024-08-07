import pandas as pd
import glob
import os
import shared_config as sc


def run_summer():
    csv_files = glob.glob(f"{sc.formatted_stats_directory}*.csv")
    if len(csv_files) == 0:
        print("No CSV files found!")
        exit()

    summed_data = []

    for file in csv_files:
        df = pd.read_csv(file)
        summed_series = df.sum()
        summed_df = summed_series.to_frame().T
        filename = os.path.basename(file)
        summed_df["filename"] = filename
        summed_df["original_row_count"] = df.shape[0]
        if "base" in filename or  "players" in filename or "pareto" in filename:
            _, terrain_type, chunkX, chunkZ, players, duration = filename.split("_")
            summed_df["chunkX"] = int(chunkX[:-1])
            summed_df["chunkZ"] = int(chunkZ[:-1])
            summed_df["active_logic"] = "activeLogic" in filename
            summed_df["Chunks"] = sc.get_circuit_chunks(
                summed_df["chunkX"], summed_df["chunkZ"], terrain_type
            )
            summed_df["players"] = int(players[:-1])
            summed_df["duration"] = int(duration.replace(".csv", "")[:-1])
            summed_df["terrain_type"] = terrain_type
        elif "gen" in filename:
            _, terrain_type, players, duration = filename.split("_")
            summed_df["terrain_type"] = terrain_type + (" (Logic Active)" if "-activeLogic" in filename else "")
            summed_df["players"] = int(players[:-1])
            summed_df["duration"] = int(duration.replace(".csv", "")[:-1])
            summed_df["Chunks"] = 25
            

        summed_data.append(summed_df)

    result_df = pd.concat(summed_data, ignore_index=True)

    result_df.to_csv(sc.summed_output, index=False)
    print("Summed CSV created successfully!")


if __name__ == "__main__":
    run_summer()
