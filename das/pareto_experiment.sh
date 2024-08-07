#!/bin/bash

# List of num_players options

source config.cfg

num_players_options=(140 140 140 140 140 140)
terrain_types=("Empty" "1-Layer" "2-Layer" "3-Layer" "4-Layer" "5-Layer") 
radius="6"
circuitX="6"
circuitZ="6"
active_logic="-activeLogic"

# Config (so I can have formatted strings)
## Folder locations
student_id="zmr280"
build_location="/var/scratch/${student_id}/"
home_folder="/home/${student_id}/"

## Build locations
build_folder="${build_location}opencraft/"
raw_executable="opencraft.x86_64"
opencraft_executable="${build_folder}${raw_executable}"
runs_dir="${build_location}runs/"
mkdir -p ${runs_dir}

## Scripts locations
net_celerity_folder="${home_folder}Net-Celerity/"
system_monitor_script="${net_celerity_folder}system_monitor.py"
client_system_monitor_script="${net_celerity_folder}client_system_monitor.py"
collect_script="${net_celerity_folder}collect_script.py"
inputtraces_folder="${net_celerity_folder}inputtraces/"

for index in "${!num_players_options[@]}"; do
    num_players2=${num_players_options[$index]}
    terrain_type2=${terrain_types[$index % 6]}
    run_config="pareto${active_logic}_${terrain_type2}_${circuitX}x_${circuitZ}z_${num_players2}p_${benchmark_duration}s"
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
    server_command="${shared_command} -terrainType ${terrain_type2} -statsFile ${server_stats} ${active_logic} -circuitX $circuitX -circuitZ $circuitZ -playType Server > ${server_log} 2>&1 &"
    ssh $server_node "${server_command}" &
    sleep 10

    server_pid=$(ssh $server_node "pgrep -f '$raw_executable'")
    echo "Starting system monitoring script on $server_node with PID $server_pid..."
    monitor_command="python3 ${system_monitor_script} ${system_logs}server.csv $server_pid"
    ssh $server_node "${monitor_command}" &

    # Starting moving clients for more circuits
    # echo "Starting moving clients on $client_node1 and $client_node2..."
    # simulation_type=" -emulationType Simulation -playerSimulationBehaviour FixedDirection "
    # client_mover_id1=202
    # client_mover_id2=204
    # client_command1="${shared_command} -serverUrl $server_ip -statsFile ${opencraft_stats}client$client_mover_id1.csv -userID $client_mover_id1 -playType Client ${simulation_type} > ${opencraft_logs}client${client_mover_id1}.log 2>&1 &"
    # client_command2="${shared_command} -serverUrl $server_ip -statsFile ${opencraft_stats}client$client_mover_id2.csv -userID $client_mover_id2 -playType Client ${simulation_type} > ${opencraft_logs}client${client_mover_id2}.log 2>&1 &"
    # ssh $client_node1 "${client_command1}" &
    # ssh $client_node2 "${client_command2}" &
    # sleep $client_interval
    # client_pid1=$(ssh $client_node1 "pgrep -f '$raw_executable'")
    # client_pid2=$(ssh $client_node2 "pgrep -f '$raw_executable'")
    # echo "client_pid1: $client_pid1, client_pid2: $client_pid2, sleeping for 20 seconds..."
    # sleep 15
    # ssh $client_node1 "pkill opencraft"
    # ssh $client_node2 "pkill opencraft"
    # sleep 2
    # ssh $client_node1 "pkill -0 opencraft" && ssh $client_node1 "pkill -9 opencraft"
    # ssh $client_node2 "pkill -0 opencraft" && ssh $client_node2 "pkill -9 opencraft"


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

    echo "Running collection script..."
    python3 $collect_script $system_logs $run_config
    wait

    echo "Benchmarking completed for ${run_config} players."
done

echo "Script execution complete."
