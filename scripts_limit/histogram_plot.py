import pandas as pd
import matplotlib.pyplot as plt
import sys
import numpy as np

if len(sys.argv) != 3:
    print("Usage: python histogram_plot tiers concurrency")
    sys.exit()

tiers = sys.argv[1].split(",")
concurrency = sys.argv[2]

BAR_COLOR = '#2ecc71'
BAR_ALPHA = 0.9
FIGURE_HEIGHT_PER_PLOT = 4

for i in range(len(tiers)):
    tier = tiers[i]
    output_name = f'{tier}_wl{concurrency}.pdf'
    datasource = f'{tier}_wl{concurrency}.csv'
    data = pd.read_csv(datasource)
    request_types = list(set(data['request_type']))

    fig, axs = plt.subplots(
        len(request_types),
        1,
        figsize=(12, FIGURE_HEIGHT_PER_PLOT * len(request_types)),
        tight_layout=True,
    )

    if len(request_types) == 1:
        axs = [axs]

    for j in range(len(request_types)):
        request_type = request_types[j]
        df_request_type = data[data['request_type'] == request_type]
        response_times = df_request_type['response_time']

        min_time = 0
        max_time = response_times.quantile(0.9999)  # Include more of the tail
        n_bins = 50

        bin_width = (max_time - min_time) / n_bins
        bins = np.linspace(min_time, max_time, n_bins + 1)

        counts, bins, patches = axs[j].hist(
            response_times,
            bins=bins,
            color=BAR_COLOR,
            alpha=BAR_ALPHA,
            edgecolor='black',
            linewidth=0.5,
            density=False
        )

        axs[j].set_yscale('log')

        axs[j].grid(True, which="both", ls="-", alpha=0.2)

        p50 = np.percentile(response_times, 50)
        p90 = np.percentile(response_times, 90)
        p99 = np.percentile(response_times, 99)
        p999 = np.percentile(response_times, 99.9)

        axs[j].axvline(p50, color='blue', linestyle='--', alpha=0.5,
                       label=f'P50: {p50:.1f}ms')
        axs[j].axvline(p90, color='orange', linestyle='--', alpha=0.5,
                       label=f'P90: {p90:.1f}ms')
        axs[j].axvline(p99, color='red', linestyle='--', alpha=0.5,
                       label=f'P99: {p99:.1f}ms')
        axs[j].axvline(p999, color='purple', linestyle='--', alpha=0.5,
                       label=f'P99.9: {p999:.1f}ms')

        axs[j].set_xlabel('Response Time [ms]', fontsize=10)
        axs[j].set_ylabel('Count (log scale)', fontsize=10)

        title = (f'{tier} {request_type}\n'
                 f'P50: {p50:.1f}ms, P90: {p90:.1f}ms, P99: {p99:.1f}ms, P99.9: {p999:.1f}ms')
        axs[j].set_title(title, fontsize=11)

        axs[j].legend(fontsize=8, loc='upper left')

        axs[j].set_xlim(min_time, max_time)

        num_ticks = 10
        tick_positions = np.linspace(min_time, max_time, num_ticks)
        axs[j].set_xticks(tick_positions)

        if max_time < 10:
            axs[j].set_xticklabels([f'{x:.3f}' for x in tick_positions], rotation=45)
        else:
            axs[j].set_xticklabels([f'{x:.0f}' for x in tick_positions], rotation=45)

        axs[j].tick_params(axis='both', which='major', labelsize=8)

        stats_text = (f'Mean: {response_times.mean():.1f}ms\n'
                      f'Std Dev: {response_times.std():.1f}ms\n'
                      f'Sample Size: {len(response_times)}')

        axs[j].text(0.95, 0.95, stats_text,
                    transform=axs[j].transAxes,
                    verticalalignment='top',
                    horizontalalignment='right',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                    fontsize=8)

    plt.tight_layout()
    plt.savefig(output_name, bbox_inches='tight', dpi=300)
    plt.close()
