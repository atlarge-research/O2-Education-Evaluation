#!/bin/bash

# Node details, benchmark duration and client interval
source config.cfg

# Used configurations
# "Empty" "1-Layer" "1-Layer" "1-Layer" "1-Layer" "1-Layer" "1-Layer" "1-Layer" "1-Layer" "1-Layer" "1-Layer" "1-Layer" "1-Layer" "1-Layer" "1-Layer" "1-Layer" "1-Layer" "1-Layer" "1-Layer" "2-Layer" "2-Layer" "2-Layer" "2-Layer" "2-Layer" "2-Layer" "3-Layer" "3-Layer" "3-Layer" "3-Layer" "3-Layer" "3-Layer" "4-Layer" "4-Layer" "5-Layer" "5-Layer" "5-Layer"
# 0 1 1 1 1 1 1 2 2 2 3 3 3 4 4 4 5 5 6 4 4 4 5 5 6 3 3 3 5 5 6 5 6 5 5 6
# 0 1 2 3 4 5 6 4 5 6 3 5 6 4 5 6 5 6 6 4 5 6 5 6 6 3 5 6 5 6 6 6 6 5 6 6

terrain_options=() # "Empty", "1-Layer" etc.
circuitXes=()      # Numbers up to 6
circuitZes=()      # Numbers up to 6
num_players=1
benchmark_duration=300

# Folder locations
build_location="/var/scratch/${student_id}/"
home_folder="/home/${student_id}/"

# Build locations
build_folder="${build_location}opencraft/"
raw_executable="opencraft.x86_64"
opencraft_executable="${build_folder}${raw_executable}"
runs_dir="${build_location}runs/"
mkdir -p ${runs_dir}

# Scripts locations
das_folder="${home_folder}das/"
system_monitor_script="${das_folder}system_monitor.py"
client_system_monitor_script="${das_folder}client_system_monitor.py"

for index in "${!terrain_options[@]}"; do
    terrain_type2=${terrain_options[$index]}
    circuitX=${circuitXes[$index]}
    circuitZ=${circuitZes[$index]}
    run_config="base-activeLogic_${terrain_type2}_${circuitX}x_${circuitZ}z_${num_players}p_${benchmark_duration}s"
    echo "Running benchmark for ${run_config} players..."

    if [[ $client_nodes_number -lt 1 ]]; then
        echo "Not enough client nodes specified. Need at least one. Exiting..."
        exit 1
    fi

    run_dir="${runs_dir}${run_config}/"
    opencraft_stats="${run_dir}opencraft_stats/"
    opencraft_logs="${run_dir}opencraft_logs/"
    system_logs="${run_dir}system_logs/"

    mkdir -p ${run_dir}
    mkdir -p ${opencraft_stats}
    mkdir -p ${opencraft_logs}
    mkdir -p ${system_logs}

    shared_command="${opencraft_executable} -batchmode -nographics -logStats True"

    # Initialising Server
    server_ip=$(ssh $server_node "hostname -I | cut -d ' ' -f1")
    server_stats="${opencraft_stats}server.csv"
    server_log="${opencraft_logs}server.log"
    echo "Starting server on $server_node at $server_ip:7777 with config ${run_config}..."
    server_command="${shared_command} -terrainType ${terrain_type2} -statsFile ${server_stats} -activeLogic -circuitX $circuitX -circuitZ $circuitZ -playType Server > ${server_log}  2>&1 &"
    ssh $server_node "${server_command}" &
    sleep 10

    server_pid=$(ssh $server_node "pgrep -f '$raw_executable'")
    echo "Starting system monitoring script on $server_node with PID $server_pid..."
    monitor_command="python3 ${system_monitor_script} ${system_logs}server.csv $server_pid"
    ssh $server_node "${monitor_command}" &

    # Initialising Client
    echo "Starting client..."
    ## Start system monitoring on client node
    client_monitor_log="${system_logs}client_node1.csv"
    ssh $client_node1 "python3 ${client_system_monitor_script} ${client_monitor_log} &" &
    ## Start client
    client_command="${shared_command} -serverUrl $server_ip -statsFile ${opencraft_stats}client1.csv -userID 1 -playType Client > ${opencraft_logs}client${i}.log 2>&1 &"
    ssh $client_node1 "${client_command1}" &
    sleep 5

    echo "Benchmarking for $benchmark_duration seconds..."
    sleep $benchmark_duration

    # Stopping the processes
    echo "Stopping system monitoring script on $server_node..."
    ssh $server_node "pkill -f 'python3 ${system_monitor_script}'"

    echo "Stopping server.. on $server_node."
    ssh $server_node "kill $server_pid"
    sleep 2
    ssh $server_node "kill -0 $server_pid" && ssh $server_node "kill -9 $server_pid"

    echo "Stopping client..."
    ssh $client_node1 "pkill -f 'python3 ${client_system_monitor_script}'"
    ssh $client_node1 "pkill opencraft"
    sleep 2
    ssh $client_node "pkill -0 opencraft" && ssh $client_node "pkill -9 opencraft"

    echo "Benchmarking completed for ${run_config} config."
done

echo "Script execution complete."
