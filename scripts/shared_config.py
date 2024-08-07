import os
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

matplotlib.rcParams.update({"font.size": 15})
plt.style.use("seaborn-v0_8-colorblind")
sns.set_palette("colorblind")

data_directory = "../data/"
experiment_name = "base_v2"
filter_by_max_terrainarea = False
filter_by_max_players = True

experiment_directory = f"{data_directory}{experiment_name}/"
formatted_stats_directory = f"{experiment_directory}formatted_stats/"
if not os.path.exists(formatted_stats_directory):
    os.makedirs(formatted_stats_directory)
plots_directory = f"../plots/"
if not os.path.exists(plots_directory):
    os.makedirs(plots_directory)

summed_output = f"{experiment_directory}summed_output.csv"
average_output = f"{experiment_directory}averaged_output.csv"

terrain_to_layer_num = {
    "Empty": 0,
    "1-Layer": 1,
    "2-Layer": 2,
    "3-Layer": 3,
    "4-Layer": 4,
    "5-Layer": 5,
    "TerrainCircuitry": 1,
    "RollingHills": 0,
}

gate_blocks_per_chunk = 32
input_blocks_per_chunk = 15

def get_circuit_chunks(chunkX, chunkZ, layer):
    return chunkX * chunkZ * terrain_to_layer_num[layer]

def get_total_circuit_blocks(chunks):
    return chunks * (gate_blocks_per_chunk + input_blocks_per_chunk)