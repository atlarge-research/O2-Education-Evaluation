import matplotlib.pyplot as plt
import numpy as np
import shared_config as sc
import os
import pandas as pd
import re


xes = []
yes = []

files = os.listdir(sc.formatted_stats_directory)
for file in files:
    if "csv" not in file:
        break
    search = re.search(r"_(\d+)-Layer_(\d+)x_(\d+)z", file)
    if search is None:
        continue
    layer, x_val, y_val = search.groups()
    layer = int(layer)
    x_val = int(x_val)
    y_val = int(y_val)
    
    y = layer * x_val * y_val
    df = pd.read_csv(f"{sc.formatted_stats_directory}{file}")
    x = df["Main Thread"] / 1e9
    
    xes.append(x)
    yes.append([y for _ in range(len(x))])
    fig, ax = plt.subplots()

    ax.hist(x, bins=8, linewidth=0.5, edgecolor="white")

    ax.set(xlim=(0, 8), xticks=np.arange(1, 8),
        ylim=(0, 56), yticks=np.linspace(0, 56, 9))

    plt.show()
    
    break