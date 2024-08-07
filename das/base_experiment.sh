#!/bin/bash

# Node details, benchmark duration and client interval
source config.cfg

terrain_options=() # "Empty", "1-Layer" etc.
active_status=() # either "" or "-activeLogic"
circuitXes=() # Numbers up to 6
circuitZes=() # Numbers up to 6
num_players=1

# Folder locations
student_id="zmr280"
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
    active_logic=${active_status[$index]}
    circuitX=${circuitXes[$index]}
    circuitZ=${circuitZes[$index]}
    run_config="base${active_logic}_${terrain_type2}_${circuitX}x_${circuitZ}z_${num_players}p_${benchmark_duration}s"
    echo "Running benchmark for ${run_config} players..."

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
    server_command="${shared_command} -terrainType ${terrain_type2} -statsFile ${server_stats} $active_logic -circuitX $circuitX -circuitZ $circuitZ -playType Server > ${server_log}  2>&1 &"
    ssh $server_node "${server_command}" &
    sleep 10

    server_pid=$(ssh $server_node "pgrep -f '$raw_executable'")
    echo "Starting system monitoring script on $server_node with PID $server_pid..."
    monitor_command="python3 ${system_monitor_script} ${system_logs}server.csv $server_pid"
    ssh $server_node "${monitor_command}" &

    # Initialising Clients
    ## Calculate number of clients per node
    clients_per_node=$((num_players / client_nodes_number))
    echo "Starting clients..."

    for node_index in $(seq 1 $client_nodes_number); do
        client_node_var="client_node$node_index"
        client_node=${!client_node_var}

        # Start system monitoring on client node
        client_monitor_log="${system_logs}client_node${node_index}.csv"
        ssh $client_node "python3 ${client_system_monitor_script} ${client_monitor_log} &" &

        start_client=$(( (node_index - 1) * clients_per_node + 1 ))
        end_client=$(( node_index * clients_per_node ))

        for i in $(seq $start_client $end_client); do
            echo "Starting client $i on $client_node..."
            simulation_type="" 
            client_command="${shared_command} -serverUrl $server_ip -statsFile ${opencraft_stats}client$i.csv -userID $i -playType Client ${simulation_type} > ${opencraft_logs}client${i}.log 2>&1 &"
            ssh $client_node "${client_command}" &
            sleep $client_interval
        done
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

    echo "Benchmarking completed for ${run_config} config."
done

echo "Script execution complete."
