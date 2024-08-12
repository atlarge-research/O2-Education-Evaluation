This repository contains the scripts used to run experiments to evaluate the [Opencraft 2 Education](https://github.com/ZainMunir/Opencraft-2-Education) project. The scripts found in `das/` were adapted from [Net-Celerity](https://github.com/atlarge-research/Net-Celerity) to run with this project as well.

# Using this repository
Experiments are designed to be run on the DAS[5](https://cs.vu.nl/das5/home.shtml)/[6](https://www.cs.vu.nl/das/) machines. 

## DAS Setup
- Many of the scripts are dependent on your studentID, so change the value found in `config.cfg`
- Move your linux build of Opencraft to `/var/scratch/student_id/`
- Move the `das/` folder to `/home/student_id/`
- Follow the linux install instructions for [miniconda](https://docs.anaconda.com/miniconda/), but change the install directory to be at `/var/scratch/student_id/`
- Navigate to the `das/` folder and create the conda environment with
    
    `conda env create -f environment.yml`
- You can manually start it with 

    `conda activate experiment-env`

- Add the above line to the end of your `.bashrc` file so it is active on start-up for every node

## Running experiments
There are 3 main experiment scripts: base, players and pareto. Each have different configuration options at the top of the file.
- Potential terrain types include "Empty", "1-Layer", "2-Layer", "3-Layer", "4-Layer", "5-Layer", "RollingHills"
- Active logic can either be "" or "-activeLogic"
- CircuitX / CircuitZ / Radius specify the dimensions of circuit generation

Nodes on DAS should be reserved via `preserve -np _ -t _` where np is the number of nodes and t is the duration they are reserved for. You may need to run `module load prun` beforehand, or you can add it to your `.bashrc` so it loads on startup. After that, you run `preserve -llist` to see which nodes you received and fill in `config.cfg` with the appropriate information.

Different experiments were run for different purposes and so loop over different parameters to run experiments in one go.

Logs from every client and the server are collected into `opencraft_logs` directories. The internal application statistics are collected into `opencraft_stats`. Each node's system statistics are collected into `system_logs`.

After running the experiments, you can then run the `get_data.sh` script locally and it will pull all the recent runs to the `data/` folder. After doing so, you can then run `clear_data.sh` on DAS so you aren't pulling the same data again

## Data
The `shared_config` file contains some parameters that most other scripts in the `scripts` directory are dependent on. The main one to consider is the `experiment_name` as that dictates which folder other scripts will look at when managing data.
### Data sanitisation
The server statistics collected start from when the server is run, rather than when the experiment begins after clients are connected. The following 3 scripts can be run in order to format the data, sum it all together and finally give an averaged csv file that other plotters will use: `data_formatter.py`, `data_summer.py` and `data_averager.py`. 
### Plotting
All plots output to the plots directory. Plots were created and adapted for the specific experiments run, so may not be compatible for other variations.

Certain scripts are designed for specific experiments while others work for all. `stacked_line_graph.py` and `stacked_bar_graph.py` work for any experiment and have an optional command-line argument `all` to include more statistics in the output. `fps_scatter.py` works for most experiments.

`bar_combined.py` and `fps_scatter_combined.py` were made specifically for players experiments and `pareto.py` for the pareto experiment.

#### Overhead
`resource_usage.py` is used to plot graphs related to overhead but `system_logs_extracter.py` should be run first to move the relevant system_logs to the `data/overhead/` directory.

