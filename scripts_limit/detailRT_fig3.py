import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# user-defined variables
#################################################################################
if len(sys.argv) != 9:
    print(
        "Usage: python detailRT_fig3.py output_name title_name x1 x2 timestamp_offset collectls hosts"
    )
    sys.exit(1)

output_name = sys.argv[1]
title_name = sys.argv[2]
x1 = sys.argv[3]
x2 = sys.argv[4]
timestamp_offset = sys.argv[5]
collectls = sys.argv[6].split(",")
collectlNW = sys.argv[7].split(",")
hosts = sys.argv[8].split(",")

num_cores = 8

collectls_cols = [
    1, 3, 4, 9, 13, 15, 16, 21, 25, 27, 28, 33, 37, 39, 40, 45, 49, 51, 52, 57, 61,
    63, 64, 69, 73, 75, 76, 81, 85, 87, 88, 93,
]

collectlNW_cols = [
    1, 2, 3, 4, 11, 12, 13, 14,
]

# Iterate over collectls
fig, axs = plt.subplots(
    len(collectls) * len(collectls_cols) + len(collectlNW) * len(collectlNW_cols),
    1,
    figsize=(9, 10 * (len(collectls) + len(collectls_cols) + len(collectlNW) + len(collectlNW_cols))),
    tight_layout=True,
)
fig.suptitle(title_name, y=0.99995)

plt.rcParams["legend.loc"] = "lower center"
count = 0

for i in range(len(collectls)):
    df = pd.read_csv(collectls[i], sep=" ", header=0)
    df.iloc[:, 0] = df.iloc[:, 0] - int(timestamp_offset)
    df = df[(df.iloc[:, 0] >= int(x1)) & (df.iloc[:, 0] <= int(x2))]

    for column in collectls_cols:
        column_name = df.columns[column]
        ax = axs[count] if isinstance(axs, np.ndarray) else axs

        ax.set_ylabel(column_name)
        ax.set_title(f"{hosts[i]}--{column_name}")
        ax.set_xlim(int(x1), int(x2))

        ax.plot(df.iloc[:, 0], df.iloc[:, column])
        ax.legend([f"{column_name} (mean={df.iloc[:, column].mean().round(4)})"], bbox_to_anchor=(0.5, -0.7),
                  frameon=False)
        count += 1

for i in range(len(collectlNW)):
    df = pd.read_csv(collectlNW[i], sep=" ", header=0)
    df.iloc[:, 0] = df.iloc[:, 0] - int(timestamp_offset)
    df = df[(df.iloc[:, 0] >= int(x1)) & (df.iloc[:, 0] <= int(x2))]

    for column in collectlNW_cols:
        column_name = df.columns[column]
        ax = axs[count] if isinstance(axs, np.ndarray) else axs

        ax.set_ylabel(column_name)
        ax.set_title(f"{hosts[i]}--{column_name}")
        ax.set_xlim(int(x1), int(x2))

        ax.plot(df.iloc[:, 0], df.iloc[:, column])
        ax.legend([f"{column_name} (mean={df.iloc[:, column].mean().round(4)})"], bbox_to_anchor=(0.5, -0.7),
                  frameon=False)
        count += 1

plt.savefig(output_name)
plt.clf()

fig, axs = plt.subplots(
    len(collectls),
    1,
    figsize=(9, 3 * len(collectls)),
    tight_layout=True,
)
fig.suptitle(title_name, y=0.9995)

count = 0
for i in range(len(collectls)):
    df_cpu = pd.read_csv(collectls[i], header=0, sep="\s+")
    df_cpu.iloc[:, 0] = df_cpu.iloc[:, 0] - int(timestamp_offset)
    df_cpu = df_cpu[(df_cpu.iloc[:, 0] >= int(x1)) & (df_cpu.iloc[:, 0] <= int(x2))]

    ax = axs[count] if isinstance(axs, np.ndarray) else axs

    for core in range(num_cores):
        column = 9 + core * 12
        ax.plot(
            df_cpu.iloc[:, 0],
            df_cpu.iloc[:, column],
            label=f"core{core} mean={df_cpu.iloc[:, column].mean().round(4)}",
        )

    ax.set_ylabel(f"VM{i}-CPU [%]")
    ax.set_xlim([int(x1), int(x2)])
    ax.legend(
        loc="lower center", bbox_to_anchor=(0.5, -0.6), ncol=3, frameon=False
    )
    ax.set_title(f"{hosts[i]}-Totl%")
    count += 1

plt.savefig(f"stacked{output_name}")
