import pandas as pd
import matplotlib.pyplot as plt
import shared_config as sc
from paretoset import paretoset

pareto_directory = f"{sc.data_directory}pareto/"
average_csv = f"{pareto_directory}averaged_output.csv"
average_df = pd.read_csv(average_csv)

category = "FPS"

x = average_df["players"]
y = average_df["Chunks"]
z = average_df[category]

fig, ax = plt.subplots()
scatter = ax.scatter(
    x, y, c=z, s=100, edgecolor="k", alpha=0.75, marker="o"
)
fig.figure.set_size_inches(10, 6)

for i in range(len(x)):
    ax.text(x[i]-2, y[i], int(z[i]), ha='right', color='lightgray')

cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label(category)


desired_values = [200, 120]

for i, desired_val in enumerate(desired_values):
    condition = function = lambda x: x >= desired_val
    filtered_df = average_df[condition(z)]
    if not filtered_df.empty:
        df = filtered_df[["Chunks", "players"]]
        mask = paretoset(df, sense=["max", "max"])
        pareto_points = filtered_df[mask]

        x = pareto_points["players"]
        y = pareto_points["Chunks"]
        
        lists = sorted(zip(*[x, y]))
        new_x, new_y = list(zip(*lists))

        ax.plot(
            new_x,
            new_y,
            linestyle="--",
            marker="o",
            markersize=5,
            label=f"{desired_val} FPS",
        )
        
        
ax.legend()

ax.set_xlabel("Players")
ax.set_ylabel("Circuits")
ax.set_xticks(range(0, max(x) + 20, 40))
# ax.set_yticks(range(0, max(y) + 18, 36))
ax.figure.tight_layout()
# plt.show()
ax.figure.savefig(f"{sc.plots_directory}pareto_front.pdf", format="pdf")
