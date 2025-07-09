import pandas as pd
import os
import glob
import time


DATA_DIR = 'data'
OUTPUT_DIR = 'data'
OUTPUT_FILENAME = 'master_transfers.parquet'

TRANSACTION_FILES = glob.glob(os.path.join(DATA_DIR, 'token_transfers*.csv'))

TOKEN_MAP = {
    '0xdac17f958d2ee523a2206206994597c13d831ec7': 'USDT',
    '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48': 'USDC',
    '0x6b175474e89094c44da98b954eedeac495271d0f': 'DAI',
    '0x8e870d67f660d95d5be530380d0ec0bd388289e1': 'PAX',
    '0xa47c8bf37f92abed4a126bda807a7b7498661acd': 'USTC',
    '0xd2877702675e6ceb975b4a1dff9fb7baf4c91ea9': 'WLUNA' 
}


def load_and_combine_data(file_list):
    """Loads multiple CSVs, concatenates them, and returns a single DataFrame."""
    print(f"Found {len(file_list)} transaction files to combine.")
    dfs = []
    for f in file_list:
        print(f"-> Loading {os.path.basename(f)}...")
        try:
            df = pd.read_csv(f)
            dfs.append(df)
        except Exception as e:
            print(f"   Error loading {f}: {e}")
            continue
    
    if not dfs:
        print("No dataframes were loaded. Exiting.")
        return None
        
    print("Combining all transaction files...")
    combined_df = pd.concat(dfs, ignore_index=True)
    return combined_df

def clean_and_enrich_data(df, token_map):
    """Performs cleaning and enrichment on the combined DataFrame."""
    print("\n--- Starting Data Cleaning and Enrichment ---")
    
    initial_rows = len(df)
    subset_cols = ['block_number', 'transaction_index', 'from_address', 'to_address', 'contract_address', 'value']
    df.drop_duplicates(subset=subset_cols, inplace=True)
    final_rows = len(df)
    print(f"Dropped {initial_rows - final_rows} duplicate rows. Final row count: {final_rows}")

    print("Converting 'time_stamp' to datetime objects...")
    df['time_stamp'] = pd.to_datetime(df['time_stamp'], unit='s')

    print("Mapping 'contract_address' to 'token_name'...")
    df['token_name'] = df['contract_address'].map(token_map)
    
    unmapped_count = df['token_name'].isnull().sum()
    if unmapped_count > 0:
        print(f"Warning: Found {unmapped_count} rows with unmapped contract addresses.")
    
    print("Sorting data by timestamp...")
    df.sort_values(by='time_stamp', inplace=True)

    print("\n--- Data Cleaning Complete ---")
    print("Data summary:")
    print(f"Date range: {df['time_stamp'].min()} to {df['time_stamp'].max()}")
    print("Token counts:")
    print(df['token_name'].value_counts(dropna=False)) 
    
    return df

def main():
    """Main execution function."""
    start_time = time.time()
    print("===== Phase 1: Data Unification and Preprocessing =====")

    raw_df = load_and_combine_data(TRANSACTION_FILES)
    
    if raw_df is None:
        return

    master_df = clean_and_enrich_data(raw_df, TOKEN_MAP)

    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
    print(f"\nSaving cleaned master data to: {output_path}")
    master_df.to_parquet(output_path, index=False)
    
    end_time = time.time()
    print("\n===== Preprocessing Complete! =====")
    print(f"The file 'master_transfers.parquet' is ready for analysis.")
    print(f"Total execution time: {end_time - start_time:.2f} seconds.")


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    main()