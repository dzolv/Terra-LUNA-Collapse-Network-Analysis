# Network Analysis of the Terra/LUNA Collapse: A Story of Panic, Centralization, and Flight to Safety

This repository contains the full analysis for the "Network Analysis and Storytelling Project" (STA404), exploring the catastrophic collapse of the Terra/LUNA ecosystem in May 2022. By constructing and analyzing daily transaction networks, this project tells a data-driven story of the market's behavior, revealing clear patterns of panic, flight to safety, and structural centralization.

The final report and analysis are presented in the `LUNA_Collapse_Network_Analysis.ipynb` Jupyter Notebook.

**[View the full analysis notebook on GitHub](LUNA_Collapse_Network_Analysis.ipynb)**

---

## Table of Contents
- [Project Overview](#project-overview)
- [Key Findings](#key-findings)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Data Source](#data-source)
  - [Installation and Setup](#installation-and-setup)
- [Project Structure](#project-structure)
- [Methodology](#methodology)

---

## Project Overview

In May 2022, the algorithmic stablecoin TerraUSD (UST) lost its $1.00 peg, triggering a hyperinflationary death spiral in its sister token, LUNA. This project analyzes a dataset of over 36 million ERC-20 token transfers on the Ethereum blockchain to answer the question:

> **How did the structure and dynamics of the transaction network reflect the catastrophic collapse?**

Using tools like Python, Pandas, NetworkX, and Gephi, we trace the flow of capital, identify key structural changes in the network, and provide quantitative evidence for the market's reaction.

## Key Findings

1.  **The Panic was Sequential and Observable:** The collapse occurred in two distinct phases visible in the on-chain data: an initial panic out of the USTC stablecoin, followed immediately by a hyperinflationary volume surge in WLUNA.
2.  **A Quantifiable "Flight to Safety":** The collapse of Terra tokens triggered a massive, quantifiable flow of capital into trusted, fiat-backed stablecoins like USDC and USDT, confirming their role as "safe haven" assets.
3.  **Panic Drives Centralization:** Under market stress, the network's structure fundamentally transformed from a relatively distributed system into a hyper-centralized, hub-and-spoke model, as panicked investors funneled all activity through a few major exchanges acting as critical "exit ramps."


## Getting Started

Follow these instructions to set up the project environment and reproduce the analysis.

### Prerequisites

- Python 3.9+
- Git and Git LFS (for handling large data files, if you choose to download them)

### Data Source

The dataset used for this project is the **ERC20 Stablecoin and WLUNA Transaction Data** provided by the Stanford Network Analysis Project (SNAP).

- **Download Link:** [https://snap.stanford.edu/data/ERC20-stablecoins.zip](https://snap.stanford.edu/data/ERC20-stablecoins.zip)

### Installation and Setup

1.  **Clone the repository.**

2.  **Set up the data directory:**
    - Create a `data/` folder in the project root.
    - Download the dataset from the link above.
    - Unzip the contents and place the raw `.csv` files inside the `data/` folder. The folder should contain `token_transfers.csv`, `token_transfers_V2.0.0.csv`, `token_transfers_V3.0.0.csv`, `event_data.csv`, and the `price_data/` subfolder.

### Execution Workflow

The analysis is split between standalone Python scripts (for heavy data processing) and the final Jupyter Notebook (for analysis and visualization). **The scripts in the `codes/` directory must be run first to generate the necessary data files for the notebook.**

Please run the scripts from the project's root directory in the following order:

**Step A: Initial Data Processing (Command Line)**

These scripts will process tens of millions of transactions and build the daily network graphs. This is the most time-consuming part.

```bash
# 1. (Optional) Validate the raw data files
python codes/validation.py

# 2. Unify, clean, and price-correct the raw transaction data
python codes/load.py

# 3. Build the sequence of daily network graphs (This will take time)
python codes/construct.py
```

**Step B: Generate Corrected Metrics (Command Line)**

This step creates the final summary CSV with accurate USD volumes, which is the primary data source for the notebook's plots.

```bash
# 4. Recalculate daily volumes with full price correction
python codes/fixTokensToUSD.py
```

**Step C: Run the Final Analysis (Jupyter Notebook)**

Now that all the necessary processed data (`master_transfers.parquet`, the daily graphs, and `daily_network_metrics_corrected.csv`) has been created, you can explore the final analysis. The purpose of using Jupyter is to better showcase other advanced analysis python code in the project and to combine it with image analysis and evaluation.

5.  **Launch Jupyter:**
    ```bash
    jupyter lab  # or jupyter notebook
    ```
6.  **Open and Run:** Open [`LUNA_Collapse_Network_Analysis.ipynb`](./LUNA_Collapse_Network_Analysis.ipynb) and run the cells from top to bottom. The notebook is designed to load the pre-processed data and will run quickly.

---

## Project Structure

The repository is organized as follows:

```
├── LUNA_Collapse_Network_Analysis.ipynb  # The main analysis and report notebook
├── README.md                             # You are here
├── requirements.txt                      # List of Python dependencies
│
├── codes/                                # Contains all the Python scripts for processing and analysis
│   ├── load.py
│   ├── construct.py
│   └── ... (and other scripts)
│
├── data/                                 # (Ignored by Git) For storing the raw and processed data
│   ├── master_transfers.parquet
│   ├── token_transfers.csv
│   └── ... (and other data files)
│
└── report/                               # Contains figures and other report assets
    ├── daily_network_metrics_corrected.csv
    ├── gephi_files/
    └── figures_notebook/
        ├── gephi_panic_day_05-09.png
        └── ... (and other plots)
```

## Methodology

The analysis follows a multi-phase approach:
1.  **Data Unification:** Combining and cleaning three large CSV files into a single, reliable master dataset.
2.  **Price Correction:** Valuating all transactions in USD by incorporating daily price data for each of the six tokens.
3.  **Dynamic Network Construction:** Building a sequence of 215 daily transaction networks to enable time-series analysis.
4.  **Time-Series Analysis:** Calculating and plotting key network metrics (node/edge counts, volume, clustering coefficient) over time to identify macro trends and anomalies.
5.  **Deep-Dive Analysis:** Performing a comparative analysis of network structure and net token flow on a "normal" day vs. a "panic" day to find microscopic evidence of behavioral shifts.
6.  **Visualization:** Using Matplotlib for quantitative plots and Gephi for intuitive network visualizations.

---

### Required Libraries and Versions

This project was built using the following key libraries. For a full list, see `requirements.txt`.

- `pandas==2.2.3`
- `numpy==2.2.6`
- `networkx==3.5`
- `matplotlib==3.10.3`
- `pyarrow==20.0.0`
- `seaborn==0.13.2`
- `tqdm==4.67.1`

