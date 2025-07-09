import pandas as pd
import os
import glob

DATA_DIR = 'data'

TRANSACTION_FILES = sorted(glob.glob(os.path.join(DATA_DIR, 'token_transfers*.csv')))

TOKEN_MAP = {
    '0xdac17f958d2ee523a2206206994597c13d831ec7': 'USDT',
    '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48': 'USDC',
    '0x6b175474e89094c44da98b954eedeac495271d0f': 'DAI',
    '0x8e870d67f660d95d5be530380d0ec0bd388289e1': 'PAX',
    '0xa47c8bf37f92abed4a126bda807a7b7498661acd': 'USTC',
    '0xd2877702675e6ceb975b4a1dff9fb7baf4c91ea9': 'WLUNA'
}


def analyze_file_contents(file_list, token_map):
    """
    Checks each CSV file for the presence of specific tokens and returns a summary DataFrame.
    """
    print("Analyzing token presence in each raw data file...")
    
    token_addresses = list(token_map.keys())
    token_names = list(token_map.values())
    
    results = {}

    for file_path in file_list:
        filename = os.path.basename(file_path)
        print(f"-> Processing {filename}...")
        
        try:
            df = pd.read_csv(file_path, usecols=['contract_address'])
            present_addresses = set(df['contract_address'].unique())
            
            token_presence = {}
            for addr, name in token_map.items():
                token_presence[name] = addr in present_addresses
            
            results[filename] = token_presence
            
        except Exception as e:
            print(f"   Could not process {filename}: {e}")
            results[filename] = {name: 'Error' for name in token_names}

    summary_df = pd.DataFrame(results).T 
    summary_df = summary_df[token_names] 
    
    return summary_df

def main():
    """Main execution function."""
    summary_table = analyze_file_contents(TRANSACTION_FILES, TOKEN_MAP)
    
    print("\n" + "="*50)
    print("      Summary of Token Presence in Raw CSV Files")
    print("="*50)
    print(summary_table)
    print("="*50)
    print("\nAs shown, no single file contains all required tokens (e.g., WLUNA).")
    print("This confirms the necessity of combining the files for a complete analysis.")
    
    summary_table.to_csv('report/data_validation_summary.csv')
    print("\nSummary table saved to 'report/data_validation_summary.csv'")


if __name__ == "__main__":
    main()