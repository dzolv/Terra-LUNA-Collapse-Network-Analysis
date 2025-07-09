import pandas as pd
import networkx as nx
import os
import time
from tqdm import tqdm

DATA_DIR = 'data'
OUTPUT_DIR = os.path.join(DATA_DIR, 'processed', 'daily_graphs')
INPUT_FILENAME = 'master_transfers.parquet'


def create_rich_graph(df_slice):
    """
    Builds a single rich, weighted, directed graph from a DataFrame slice.
    Edge attributes are dictionaries of token-value pairs.
    Example edge data: { 'USDT': 500.0, 'WLUNA': 10000.0 }
    """
    if df_slice.empty:
        return nx.DiGraph()

    edge_list = df_slice.groupby(['from_address', 'to_address', 'token_name'])['value'].sum().reset_index()
    
    G = nx.DiGraph()
    
    for _, row in edge_list.iterrows():
        source = row['from_address']
        target = row['to_address']
        token = row['token_name']
        weight = row['value']
        
        if G.has_edge(source, target):
            G[source][target][token] = G[source][target].get(token, 0) + weight
        else:
            G.add_edge(source, target, **{token: weight})
            
    return G

def main():
    """
    Main execution function to loop through days and generate a graph for each.
    """
    start_time = time.time()
    print("===== Phase 2 (Dynamic): High-Frequency Network Construction =====")

    input_path = os.path.join(DATA_DIR, INPUT_FILENAME)
    if not os.path.exists(input_path):
        print(f"Error: Master data file not found at {input_path}")
        print("Please run '01_data_preprocessing.py' first.")
        return
        
    print(f"Loading master data from {input_path}...")
    df = pd.read_parquet(input_path)
    
    df['time_stamp'] = pd.to_datetime(df['time_stamp'])
    df.set_index('time_stamp', inplace=True)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Daily graphs will be saved to: {OUTPUT_DIR}")

    start_date = df.index.min().date()
    end_date = df.index.max().date()
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    print(f"Generating daily graphs from {start_date} to {end_date}...")

    for current_date in tqdm(date_range, desc="Processing Days"):
        date_str = current_date.strftime('%Y-%m-%d')
        
        daily_df = df.loc[date_str]
        
        if daily_df.empty:
            continue
            
        G_daily = create_rich_graph(daily_df)
        
        output_filename = f"graph_{date_str}.gexf"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        try:
            nx.write_gexf(G_daily, output_path)
        except Exception as e:
            print(f"\nError saving graph for {date_str}: {e}")

    end_time = time.time()
    print("\n===== Dynamic Network Construction Complete! =====")
    print(f"All daily graphs have been built and saved.")
    print(f"Total execution time: {time.strftime('%H:%M:%S', time.gmtime(end_time - start_time))}")


if __name__ == "__main__":
    main()