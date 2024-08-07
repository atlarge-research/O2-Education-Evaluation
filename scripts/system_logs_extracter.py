import os
import re
import shared_config as sc
import shutil


player_experiments = [
    f"{sc.data_directory}{x}/"
    for x in os.listdir(sc.data_directory)
    if "players" in x and not "TerrainCircuitry" in x and not "Dummy" in x  
]

overhead_directory = f"{sc.data_directory}overhead/"
os.makedirs(overhead_directory, exist_ok=True)

for experiment in player_experiments:
    experiment_name = re.search(r"players(.+)", experiment).group(1)
    experiment_directory = f"{overhead_directory}players{experiment_name}/"
    os.makedirs(experiment_directory, exist_ok=True)
    
    for run in os.listdir(experiment):
        if "players" not in run:
            continue
        system_logs = f"{experiment}{run}/system_logs/"
        for log in os.listdir(system_logs):
            output_file = f"{experiment_directory}{run}_{log}"
            # print(f"Copying {log} to {output_file}")
            shutil.copyfile(f"{system_logs}{log}", output_file)    