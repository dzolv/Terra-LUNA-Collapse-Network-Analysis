import pandas as pd
import networkx as nx
import os
import glob
from tqdm import tqdm
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import time

GRAPH_DIR = os.path.join('data', 'processed', 'daily_graphs')
OUTPUT_DIR = 'report'
FIGURES_DIR = os.path.join(OUTPUT_DIR, 'figures', 'timeseries')


def analyze_graph(graph):
    """Calculates a dictionary of metrics for a single graph."""
    metrics = {
        'nodes': graph.number_of_nodes(),
        'edges': graph.number_of_edges(),
        'avg_clustering': 0, 
        'volume_wluna': 0,
        'volume_ustc': 0,
        'volume_usdc': 0,
        'volume_usdt': 0,
        'volume_total': 0
    }

    if metrics['nodes'] == 0:
        return metrics

    try:
        metrics['avg_clustering'] = nx.average_clustering(graph)
    except Exception:
        pass

    for _, _, data in graph.edges(data=True):
        wluna_val = data.get('WLUNA', 0)
        ustc_val = data.get('USTC', 0)
        usdc_val = data.get('USDC', 0)
        usdt_val = data.get('USDT', 0)
        
        metrics['volume_wluna'] += wluna_val
        metrics['volume_ustc'] += ustc_val
        metrics['volume_usdc'] += usdc_val
        metrics['volume_usdt'] += usdt_val
        metrics['volume_total'] += wluna_val + ustc_val + usdc_val + usdt_val
        
    return metrics

def plot_time_series(df, columns, title, ylabel, filename):
    """Generic function to plot time series data."""
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(15, 7))
    
    for col in columns:
        ax.plot(df.index, df[col], label=col)
    
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    
    crisis_start = '2022-05-08'
    crisis_end = '2022-05-20'
    ax.axvspan(crisis_start, crisis_end, color='red', alpha=0.2, label='Crisis Period (May 8-20)')
    
    ax.set_title(title, fontsize=16)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_xlabel("Date", fontsize=12)
    ax.legend()
    fig.autofmt_xdate()
    
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved plot: {filename}")


def main():
    start_time = time.time()
    print("===== Phase 3: Time-Series Metric Analysis =====")
    
    os.makedirs(FIGURES_DIR, exist_ok=True)
    
    graph_files = sorted(glob.glob(os.path.join(GRAPH_DIR, 'graph_*.gexf')))
    
    if not graph_files:
        print(f"Error: No graph files found in {GRAPH_DIR}")
        return

    daily_metrics = []
    dates = []

    for g_file in tqdm(graph_files, desc="Analyzing daily graphs"):
        date_str = os.path.basename(g_file).replace('graph_', '').replace('.gexf', '')
        dates.append(pd.to_datetime(date_str))
        
        G = nx.read_gexf(g_file)
        
        metrics = analyze_graph(G)
        daily_metrics.append(metrics)

    metrics_df = pd.DataFrame(daily_metrics, index=dates)
    
    metrics_df['volume_safe_stables'] = metrics_df['volume_usdc'] + metrics_df['volume_usdt']
    
    output_csv_path = os.path.join(OUTPUT_DIR, 'daily_network_metrics.csv')
    metrics_df.to_csv(output_csv_path)
    print(f"\nDaily metrics saved to {output_csv_path}")

    print("\nGenerating time-series plots...")
    
    # Plot 1: Network Activity (Nodes and Edges)
    plot_time_series(metrics_df, ['nodes', 'edges'], 
                     'Daily Network Activity', 'Count',
                     os.path.join(FIGURES_DIR, 'daily_activity.png'))

    # Plot 2: LUNA/USTC Transaction Volume
    plot_time_series(metrics_df, ['volume_wluna', 'volume_ustc'], 
                     'Daily Transaction Volume of Terra Ecosystem Tokens', 'Volume (in USD)',
                     os.path.join(FIGURES_DIR, 'daily_volume_terra.png'))

    # Plot 3: "Flight to Safety" Volume
    plot_time_series(metrics_df, ['volume_safe_stables'], 
                     'Daily Transaction Volume of "Safe" Stablecoins (USDC+USDT)', 'Volume (in USD)',
                     os.path.join(FIGURES_DIR, 'daily_volume_safe_stables.png'))
                     
    # Plot 4: Average Clustering Coefficient
    plot_time_series(metrics_df, ['avg_clustering'], 
                     'Daily Average Clustering Coefficient', 'Clustering Coefficient',
                     os.path.join(FIGURES_DIR, 'daily_avg_clustering.png'))

    end_time = time.time()
    print("\n===== Time-Series Analysis Complete! =====")
    print(f"Total execution time: {time.time() - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()