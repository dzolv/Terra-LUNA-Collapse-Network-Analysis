import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

INPUT_CSV = os.path.join('report', 'daily_network_metrics_corrected.csv')
FIGURES_DIR = os.path.join('report', 'figures', 'timeseries_corrected')
os.makedirs(FIGURES_DIR, exist_ok=True)

def plot_time_series(df, columns, title, ylabel, filename, use_log_scale=False):
    """Generic function to plot time series data, with an option for log scale."""
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(15, 7))
    
    for col in columns:
        plot_col = col.replace('volume_', '').upper() if 'volume_' in col else col
        ax.plot(df.index, df[col], label=plot_col)
    
    if use_log_scale:
        ax.set_yscale('log')
        ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:,.0f}"))
        ylabel += " (Log Scale)"

    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    
    crisis_start = '2022-05-08'
    crisis_end = '2022-05-20'
    ax.axvspan(pd.to_datetime(crisis_start), pd.to_datetime(crisis_end), color='red', alpha=0.2, label='Crisis Period')
    
    ax.set_title(title, fontsize=16)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_xlabel("Date", fontsize=12)
    ax.legend()
    fig.autofmt_xdate()
    
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved plot: {filename}")


def main():
    print("===== Generating Corrected Time-Series Plots =====")
    
    metrics_df = pd.read_csv(INPUT_CSV, index_col=0, parse_dates=True)
    
    metrics_df['volume_safe_stables'] = metrics_df['volume_usdc'] + metrics_df['volume_usdt']
    
    print("Generating new plots from corrected data...")

    # Plot 1: Network Activity (Nodes and Edges) - Unchanged
    plot_time_series(metrics_df, ['nodes', 'edges'], 
                     'Daily Network Activity', 'Count',
                     os.path.join(FIGURES_DIR, 'daily_activity_corrected.png'))

    # Plot 2: LUNA/USTC Transaction Volume - This is the critical one
    plot_time_series(metrics_df, ['volume_wluna', 'volume_ustc'], 
                     'Daily Transaction Volume of Terra Ecosystem Tokens (USD)', 'Volume (USD)',
                     os.path.join(FIGURES_DIR, 'daily_volume_terra_corrected.png'),
                     use_log_scale=True) # Using log scale!

    # Plot 3: "Flight to Safety" Volume
    plot_time_series(metrics_df, ['volume_safe_stables'], 
                     'Daily Transaction Volume of "Safe" Stablecoins (USDC+USDT)', 'Volume (USD)',
                     os.path.join(FIGURES_DIR, 'daily_volume_safe_stables_corrected.png'))
                     
    # Plot 4: Average Clustering Coefficient - Unchanged
    plot_time_series(metrics_df, ['avg_clustering'], 
                     'Daily Average Clustering Coefficient', 'Clustering Coefficient',
                     os.path.join(FIGURES_DIR, 'daily_avg_clustering_corrected.png'))
                     
    print("\n===== Plot Generation Complete! =====")
    print(f"New plots saved in: {FIGURES_DIR}")

if __name__ == "__main__":
    main()