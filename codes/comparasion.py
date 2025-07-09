import pandas as pd
import networkx as nx
import os
import matplotlib.pyplot as plt
import numpy as np
import time

DATA_DIR = 'data'
GRAPH_DIR = os.path.join(DATA_DIR, 'processed', 'daily_graphs')
OUTPUT_DIR = os.path.join('report', 'figures', 'deep_dive_corrected')
os.makedirs(OUTPUT_DIR, exist_ok=True)

DATE_NORMAL = '2022-05-04'
DATE_PANIC = '2022-05-09'

MASTER_DF = pd.read_parquet(os.path.join(DATA_DIR, 'master_transfers.parquet'))
MASTER_DF['date'] = pd.to_datetime(MASTER_DF['time_stamp']).dt.date

PRICE_DF_WLUNA = pd.read_csv(os.path.join(DATA_DIR, 'price_data', 'wluna_price_data.csv'))
PRICE_DF_WLUNA['date'] = pd.to_datetime(PRICE_DF_WLUNA['timestamp'], unit='s').dt.date


def analyze_hub_net_flow_corrected(hub_address, date_str):
    """
    Calculates the USD net flow for a hub on a specific day by
    querying the master dataframe directly and applying price correction for WLUNA.
    """
    print(f"  -> Analyzing net flow for {hub_address[:10]}... on {date_str}")
    
    target_date = pd.to_datetime(date_str).date()
    day_df = MASTER_DF[MASTER_DF['date'] == target_date]
    
    try:
        day_price_wluna = PRICE_DF_WLUNA[PRICE_DF_WLUNA['date'] == target_date]['close'].iloc[0]
    except IndexError:
        print(f"    Warning: No price found for WLUNA on {date_str}. Using 0.")
        day_price_wluna = 0

    net_flow = {'WLUNA': 0, 'USTC': 0, 'USDC': 0, 'USDT': 0}
    
    in_df = day_df[day_df['to_address'] == hub_address]
    out_df = day_df[day_df['from_address'] == hub_address]
    
    for token in net_flow:
        in_value = in_df[in_df['token_name'] == token]['value'].sum()
        out_value = out_df[out_df['token_name'] == token]['value'].sum()
        
        if token == 'WLUNA':
            in_value *= day_price_wluna
            out_value *= day_price_wluna
        
        net_flow[token] = in_value - out_value
        
    return net_flow

def plot_degree_distribution(G, date_str, ax):
    """Plots the log-log degree distribution."""
    degrees = [d for n, d in G.degree() if d > 0]
    if not degrees: return
    
    max_deg = max(degrees)
    if max_deg < 2: return
    bins = np.logspace(np.log10(1), np.log10(max_deg), 30)
    
    hist, bin_edges = np.histogram(degrees, bins=bins, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    non_zero = hist > 0
    ax.loglog(bin_centers[non_zero], hist[non_zero], 'o', alpha=0.7, label=f'Degree Dist ({date_str})')
    ax.set_xlabel("Degree (k)")
    ax.set_ylabel("Probability Density P(k)")
    ax.set_title("Degree Distribution Comparison")
    ax.grid(True, which="both", ls="--")
    ax.legend()



def main():
    print("===== Final Deep Dive Comparison (Corrected) =====")
    
    G_normal_path = os.path.join(GRAPH_DIR, f"graph_{DATE_NORMAL}.gexf")
    G_panic_path = os.path.join(GRAPH_DIR, f"graph_{DATE_PANIC}.gexf")
    
    print(f"Loading NORMAL day graph for structural analysis: {DATE_NORMAL}")
    G_normal = nx.read_gexf(G_normal_path)
    print(f"Loading PANIC day graph for structural analysis: {DATE_PANIC}")
    G_panic = nx.read_gexf(G_panic_path)
    
    hub_to_analyze = '0x56178a0d5f301baf6cf3e1cd53d9863437345bf9' # Binance 8 Wallet
    print(f"\n>>> Analyzing Net Flow for Key CEX Wallet: {hub_to_analyze}")

    flow_normal = analyze_hub_net_flow_corrected(hub_to_analyze, DATE_NORMAL)
    flow_panic = analyze_hub_net_flow_corrected(hub_to_analyze, DATE_PANIC)

    df_flow = pd.DataFrame([flow_normal, flow_panic], index=[DATE_NORMAL, DATE_PANIC])
    print("\nNet Flow Table (Positive = Net In-flow)")
    print(df_flow.to_string(float_format=lambda x: f"{x:,.0f}"))
    
    fig, ax = plt.subplots(figsize=(12, 7))
    df_flow.plot(kind='bar', ax=ax, rot=0)
    ax.set_title(f'Token Net Flow for Binance 8 Wallet', fontsize=16)
    ax.set_ylabel('Net Volume (USD)')
    ax.axhline(0, color='black', linewidth=0.8)
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
    plt.tight_layout()
    plot_path = os.path.join(OUTPUT_DIR, 'binance_hub_net_flow.png')
    plt.savefig(plot_path, dpi=300)
    print(f"\nSaved plot: {plot_path}")
    plt.close(fig)

    print("\n--- Comparing Degree Distributions ---")
    fig, ax = plt.subplots(figsize=(10, 7))
    plot_degree_distribution(G_normal, DATE_NORMAL, ax)
    plot_degree_distribution(G_panic, DATE_PANIC, ax)
    plot_path = os.path.join(OUTPUT_DIR, 'degree_distribution_comparison_corrected.png')
    plt.savefig(plot_path, dpi=300)
    print(f"Saved plot: {plot_path}")
    plt.close(fig)
    
    print("\n===== Project Analysis Complete! =====")

if __name__ == "__main__":
    main()