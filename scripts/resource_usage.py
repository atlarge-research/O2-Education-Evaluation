import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re
import shared_config as sc
import matplotlib

def sort_list2_by_list1(list1, list2):
    order_dict = {value: index for index, value in enumerate(list1)}

    def extract_key(item):
        key_part = item.split(".")[0]
        return order_dict.get(key_part, float("inf"))

    sorted_list2 = sorted(list2, key=extract_key)

    return sorted_list2


options = [
    {
        "name": "Memory Usage",
        "addition": "memory",
        "client_column_name": "rss",
        "server_column_name": "proc.memory_info.rss",
        "units": "GB",
        "clients_data": True,
    },
    {
        "name": "CPU Usage",
        "addition": "cpu",
        "client_column_name": "cpu_percent",
        "server_column_name": "proc.cpu_percent",
        "units": "%",
        "clients_data": True,
    },
    {
        "name": "Network Sent",
        "addition": "network_sent",
        "client_column_name": "",
        "server_column_name": "net.bytes_sent",
        "units": "MB/s",
        "clients_data": False,
    },
    {
        "name": "Network Received",
        "addition": "network_recv",
        "client_column_name": "",
        "server_column_name": "net.bytes_recv",
        "units": "MB/s",
        "clients_data": False,
    },
]

order = [
    "Flat",
    "Flat (Logic Active)",
    "2-Layer (Logic Active)",
    "RollingHills",
    "RollingHills (Logic Active)",
]

for option in options:

    name = option["name"]
    addition = option["addition"]
    client_column_name = option["client_column_name"]
    server_column_name = option["server_column_name"]
    units = option["units"]
    clients_data = option["clients_data"]

    overhead_directory = f"{sc.data_directory}overhead/"

    experiments = [
        d
        for d in os.listdir(overhead_directory)
        if os.path.isdir(os.path.join(overhead_directory, d))
    ]

    experiment_averages = {}
    server_averages = {}

    for experiment in experiments:
        experiment_directory = f"{overhead_directory}{experiment}/"
        search = re.search(r"players(.+)", experiment)
        if search:
            val = search.group(1)
            if "-activeLogic" in val:
                val = f"{val.replace('-activeLogic_', '').replace('Empty', 'Flat')} (Logic Active)"
            else:
                val = val.replace("_", "").replace('Empty', 'Flat')
        else:
            raise ValueError(f"Invalid experiment name: {experiment}")

        combinations = {}
        active_logic = False
        duration = 0
        for run in os.listdir(experiment_directory):
            run_path = f"{experiment_directory}{run}"
            if not active_logic:
                active_logic = "-activeLogic" in run
            if duration == 0 or duration is None:
                duration = int(re.search(r"_(\d+)s", run).group(1))
                

            player_num = re.search(r"_(\d+)p", run).group(1)
            
            if int(player_num) > 100:
                continue
            if player_num not in combinations:
                combinations[player_num] = {
                    "server": None,
                    "clients": [],
                }
            if "server" in run:
                combinations[player_num]["server"] = run_path
            if "client" in run:
                combinations[player_num]["clients"].append(run_path)

        client_averages = {}
        server_averages_per_experiment = {}

        sorted_combinations = sorted(combinations.items(), key=lambda x: int(x[0]))

        for key, value in sorted_combinations:
            client_csv_files = value["clients"]
            server_csv_file = value["server"]

            if clients_data:
                client_data_frames = [
                    pd.read_csv(csv_file) for csv_file in client_csv_files
                ]
                client_column_values = pd.concat(
                    [df.tail(duration)[client_column_name] for df in client_data_frames]
                )
                client_averages[int(key)] = client_column_values.mean()
                if "memory" in addition:
                    client_averages[int(key)] /= 1024**3

            server_data_frame = pd.read_csv(server_csv_file, sep=";")
            server_data_frame = server_data_frame.tail(duration)
            server_column_values = server_data_frame[
                [
                    col
                    for col in server_data_frame.columns
                    if col.startswith(server_column_name)
                ]
            ].sum(axis=1)
            if "network" in addition:
                server_column_values = np.diff(server_column_values) / 1024**2
            server_averages_per_experiment[int(key)] = server_column_values.mean()
            if "memory" in addition:
                server_averages_per_experiment[int(key)] /= 1024**3

        experiment_averages[val] = client_averages
        server_averages[val] = server_averages_per_experiment

    experiments = sort_list2_by_list1(order, list(server_averages.keys()))

    all_player_nums = sorted(
        {
            player_num
            for averages in server_averages.values()
            for player_num in averages.keys()
        }
    )

    output_file = f"{sc.plots_directory}overhead_{addition}"

    bar_width = 1 / (len(experiments) + 1)
    index = np.arange(len(all_player_nums))

    matplotlib.rcParams.update({"font.size": 22})

    if clients_data:
        # Plotting client usage
        plt.figure(figsize=(10, 7))
        plt.tight_layout()

        client_sum_averages = np.zeros(len(all_player_nums))
        for i, experiment in enumerate(experiments):
            averages = experiment_averages[experiment]
            values = [averages.get(player_num, 0) for player_num in all_player_nums]
            client_sum_averages += np.array(values)
            plt.bar(index + i * bar_width, values, bar_width, label=experiment)

        client_avg_values = client_sum_averages / len(experiments)
        plt.plot(index + bar_width * (len(experiments) - 1) / 2, client_avg_values, color='gray', linestyle='-', label='_nolegend_')

        plt.xlabel("Number of Players")
        plt.ylabel(f"{name} ({units}) (Client)")
        plt.xticks(index + bar_width * (len(experiments) - 1) / 2, all_player_nums)
        
        
        
        if "CPU" in name:
            plt.legend(reverse=True, loc="lower right")
        else:
            plt.legend(reverse=True, framealpha=0.0)
        

        # plt.show()
        plt.savefig(f"{output_file}_client.pdf", format="pdf")
        print(f"Saved to {output_file}_client.pdf")

    # Plotting server usage
    plt.figure(figsize=(10, 7))
    plt.tight_layout()

    server_sum_averages = np.zeros(len(all_player_nums))

    for i, experiment in enumerate(experiments):
        averages = server_averages[experiment]
        values = [averages.get(player_num, 0) for player_num in all_player_nums]
        server_sum_averages += np.array(values)
        plt.bar(index + i * bar_width, values, bar_width, label=experiment)

    server_avg_values = server_sum_averages / len(experiments)

    plt.plot(index + bar_width * (len(experiments) - 1) / 2, server_avg_values, color='gray', linestyle='-', label='_nolegend_')

    plt.xlabel("Number of Players")
    plt.ylabel(f"{name} ({units}) (Server)")
    plt.xticks(index + bar_width * (len(experiments) - 1) / 2, all_player_nums)
    plt.legend(reverse=True, framealpha=0.0)

    # plt.show()
    plt.savefig(f"{output_file}_server.pdf", format="pdf")
    print(f"Saved to {output_file}_server.pdf")
    
    
    # server_averages_df = pd.DataFrame(server_averages)
    # server_averages_df.to_csv(f"{output_file}_server.csv", sep=";")