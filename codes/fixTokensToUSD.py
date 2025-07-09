import pandas as pd
import os
import time

DATA_DIR = 'data'
REPORT_DIR = 'report'
MASTER_FILE = os.path.join(DATA_DIR, 'master_transfers.parquet')
OUTPUT_CSV = os.path.join(REPORT_DIR, 'daily_network_metrics_corrected.csv')

PRICE_FILES = {
    'WLUNA': os.path.join(DATA_DIR, 'price_data', 'wluna_price_data.csv'),
    'USDT': os.path.join(DATA_DIR, 'price_data', 'usdt_price_data.csv'),
    'USDC': os.path.join(DATA_DIR, 'price_data', 'usdc_price_data.csv'),
    'DAI': os.path.join(DATA_DIR, 'price_data', 'dai_price_data.csv'),
    'USTC': os.path.join(DATA_DIR, 'price_data', 'ustc_price_data.csv'),
    'PAX': os.path.join(DATA_DIR, 'price_data', 'pax_price_data.csv'),
}


def load_all_price_data(price_file_map):
    """Loads all price data files and combines them into a single DataFrame."""
    all_prices = []
    print("Loading all price data files...")
    for token_name, file_path in price_file_map.items():
        try:
            price_df = pd.read_csv(file_path)
            price_df['token_name'] = token_name
            all_prices.append(price_df)
        except FileNotFoundError:
            print(f"  -> Warning: Price file not found for {token_name} at {file_path}. Skipping.")
            continue
            
    combined_prices = pd.concat(all_prices, ignore_index=True)
    combined_prices['date'] = pd.to_datetime(combined_prices['timestamp'], unit='s').dt.date
    return combined_prices[['date', 'token_name', 'close']].rename(columns={'close': 'price'})

def main():
    start_time = time.time()
    print("===== Recalculating Daily Volumes with Full Price Correction =====")
    
    print("\nLoading master transaction data...")
    df = pd.read_parquet(MASTER_FILE)
    df['date'] = pd.to_datetime(df['time_stamp']).dt.date
    
    price_df = load_all_price_data(PRICE_FILES)

    print("\nApplying price correction to all transactions...")
    
    merged_df = pd.merge(df, price_df, on=['date', 'token_name'], how='left')
    
    merged_df['price'] = merged_df.groupby('token_name')['price'].ffill()
    merged_df['price'].fillna(1.0, inplace=True) # As a final fallback, assume a price of 1.0 for any remaining NaNs

    merged_df['usd_value'] = merged_df['value'] * merged_df['price']
    
    print("Price correction complete.")
    
    print("\nAggregating daily volumes...")
    daily_volumes = merged_df.groupby(['date', 'token_name'])['usd_value'].sum().unstack(fill_value=0)
    
    daily_volumes = daily_volumes.rename(columns={
        'WLUNA': 'volume_wluna',
        'USTC': 'volume_ustc',
        'USDC': 'volume_usdc',
        'USDT': 'volume_usdt',
        'DAI': 'volume_dai',
        'PAX': 'volume_pax'
    })
    
    print("Combining with structural metrics from previous analysis...")
    try:
        old_metrics_df = pd.read_csv(os.path.join(REPORT_DIR, 'daily_network_metrics.csv'), index_col=0, parse_dates=True)
        final_df = old_metrics_df[['nodes', 'edges', 'avg_clustering']].join(daily_volumes, how='left').fillna(0)
    except FileNotFoundError:
        print("  -> Warning: 'daily_network_metrics.csv' not found. Creating a new file with only volume data.")
        final_df = daily_volumes

    final_df.to_csv(OUTPUT_CSV)
    
    print(f"\nFully corrected daily metrics saved to {OUTPUT_CSV}")
    print(f"Total execution time: {time.time() - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()