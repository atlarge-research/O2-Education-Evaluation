#!/bin/bash

# Node details, benchmark duration and client interval
source config.cfg

# Used configurations
# 120 160 200 40 80 120 160 200 40 80 120 160 200 40 80 120 160 200 40 80 120 40 80 120 160 200 40 80 120 160 200 40 80 120 160 200 40 80 120 160 40 80 120 160 200 40 80
# "1-Layer" "1-Layer" "1-Layer" "1-Layer" "1-Layer" "2-Layer" "2-Layer" "2-Layer" "2-Layer" "2-Layer" "3-Layer" "3-Layer" "3-Layer" "3-Layer" "3-Layer" "4-Layer" "4-Layer" "4-Layer" "4-Layer" "4-Layer" "5-Layer" "5-Layer" "5-Layer" "5-Layer" "5-Layer" "5-Layer" "5-Layer" "5-Layer" "5-Layer" "5-Layer" "5-Layer" "5-Layer" "5-Layer" "5-Layer" "5-Layer" "5-Layer" "5-Layer" "5-Layer" "5-Layer" "5-Layer" "5-Layer" "5-Layer" "Empty" "Empty" "Empty" "Empty" "Empty"
# 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 10 10 10 6 6 6 6 6 7 7 7 7 7 8 8 8 8 8 9 9 9 9 0 0 0 0 0
# 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 0 0 0 0 0

num_players_options=() # Increments of 40 usually
terrain_types=()       # "Empty", "1-Layer" etc.
circuitXes=()          # Numbers up to 10
circuitZes=()          # Numbers up to 6
benchmark_duration=120

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

for index in "${!num_players_options[@]}"; do
    num_players2=${num_players_options[$index]}
    terrain_type2=${terrain_types[$index]}
    circuitX=${circuitXes[$index]}
    circuitZ=${circuitZes[$index]}
    run_config="pareto-activeLogic_${terrain_type2}_${circuitX}x_${circuitZ}z_${num_players2}p_${benchmark_duration}s"
    # echo "Running benchmark for ${run_config} players..."

    if [[ $client_nodes_number -lt 10 ]]; then
        echo "Not enough client nodes specified. Need all 10. Exiting..."
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
    server_command="${shared_command} -terrainType ${terrain_type2} -statsFile ${server_stats} -activeLogic -circuitX $circuitX -circuitZ $circuitZ -playType Server > ${server_log} 2>&1 &"
    ssh $server_node "${server_command}" &
    sleep 10

    server_pid=$(ssh $server_node "pgrep -f '$raw_executable'")
    echo "Starting system monitoring script on $server_node with PID $server_pid..."
    monitor_command="python3 ${system_monitor_script} ${system_logs}server.csv $server_pid"
    ssh $server_node "${monitor_command}" &

    if [[ $circuitX -gt 6 ]]; then
        # Starting moving clients for more circuits (if circuitX > 6)
        echo "Starting moving clients on $client_node1 and $client_node2..."
        simulation_type=" -emulationType Simulation -playerSimulationBehaviour FixedDirection "
        client_mover_id1=202
        client_mover_id2=204
        client_command1="${shared_command} -serverUrl $server_ip -statsFile ${opencraft_stats}client$client_mover_id1.csv -userID $client_mover_id1 -playType Client ${simulation_type} > ${opencraft_logs}client${client_mover_id1}.log 2>&1 &"
        client_command2="${shared_command} -serverUrl $server_ip -statsFile ${opencraft_stats}client$client_mover_id2.csv -userID $client_mover_id2 -playType Client ${simulation_type} > ${opencraft_logs}client${client_mover_id2}.log 2>&1 &"
        ssh $client_node1 "${client_command1}" &
        ssh $client_node2 "${client_command2}" &
        sleep $client_interval
        client_pid1=$(ssh $client_node1 "pgrep -f '$raw_executable'")
        client_pid2=$(ssh $client_node2 "pgrep -f '$raw_executable'")
        echo "client_pid1: $client_pid1, client_pid2: $client_pid2, sleeping for 20 seconds..."
        sleep 15
        ssh $client_node1 "pkill opencraft"
        ssh $client_node2 "pkill opencraft"
        sleep 2
        ssh $client_node1 "pkill -0 opencraft" && ssh $client_node1 "pkill -9 opencraft"
        ssh $client_node2 "pkill -0 opencraft" && ssh $client_node2 "pkill -9 opencraft"
    fi

    # Initialising Clients
    ## Calculate number of clients per node
    echo "Starting clients..."
    for i in $(seq 1 $num_players2); do
        node_index=$((((i - 1) % client_nodes_number) + 1))
        client_node_var="client_node$node_index"
        client_node=${!client_node_var}

        # If this is the first client on the node, start system monitoring
        if ((((i - 1) / client_nodes_number) == 0)); then
            client_monitor_log="${system_logs}client_node${node_index}.csv"
            echo "Starting system monitoring script on $client_node..."
            ssh $client_node "python3 ${client_system_monitor_script} ${client_monitor_log} &" &
        fi

        echo "Starting client $i on $client_node..."
        simulation_type=" -emulationType Simulation "
        client_command="${shared_command} -serverUrl $server_ip -statsFile ${opencraft_stats}client$i.csv -userID $i -playType Client ${simulation_type} > ${opencraft_logs}client${i}.log 2>&1 &"
        ssh $client_node "${client_command}" &

        if ((client_nodes_number == node_index)); then
            echo "Sleeping for $client_interval seconds..."
            sleep $client_interval
        fi
    done

    sleep 5

    echo "Benchmarking for $benchmark_duration seconds..."
    sleep $benchmark_duration

    echo "Stopping system monitoring script on $server_node..."
    ssh $server_node "pkill -f 'python3 ${system_monitor_script}'"

    echo "Stopping server.. on $server_node."
    ssh $server_node "kill $server_pid"
    sleep 2
    ssh $server_node "kill -0 $server_pid" && ssh $server_node "kill -9 $server_pid"

    echo "Stopping clients..."
    for node_index in $(seq 1 $client_nodes_number); do
        # Stop system monitoring on client node
        ssh $client_node "pkill -f 'python3 ${client_system_monitor_script}'"

        client_node_var="client_node$node_index"
        client_node=${!client_node_var}
        ssh $client_node "pkill opencraft"
        sleep 2
        ssh $client_node "pkill -0 opencraft" && ssh $client_node "pkill -9 opencraft"
        echo "Stopped clients on $client_node."
    done

    echo "Benchmarking completed for ${run_config} players."
done

echo "Script execution complete."
