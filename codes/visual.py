import networkx as nx
import pandas as pd
import os

GRAPH_DIR = os.path.join('data', 'processed', 'daily_graphs')
GEPHI_DIR = os.path.join('report', 'gephi_files')
os.makedirs(GEPHI_DIR, exist_ok=True)

DATES = ['2022-05-04', '2022-05-09']
TOP_N_EDGES = 2000 

def create_top_n_edge_graph(g_rich, n):
    """
    Creates a new graph containing only the top N edges by weight.
    """
    if g_rich.number_of_edges() == 0:
        return nx.DiGraph()

    edge_weights = []
    for u, v, data in g_rich.edges(data=True):
        total_weight = sum(w for w in data.values() if isinstance(w, (int, float)))
        if total_weight > 0:
            edge_weights.append((u, v, total_weight))
            
    n = min(n, len(edge_weights))

    top_edges = sorted(edge_weights, key=lambda x: x[2], reverse=True)[:n]
    
    g_top = nx.DiGraph()
    for u, v, weight in top_edges:
        g_top.add_edge(u, v, weight=weight)
        
    return g_top

for date_str in DATES:
    print(f"--- Processing graph for {date_str} ---")
    
    g_rich_path = os.path.join(GRAPH_DIR, f"graph_{date_str}.gexf")
    g_rich = nx.read_gexf(g_rich_path)
    
    g_filtered = create_top_n_edge_graph(g_rich, TOP_N_EDGES)
    
    print(f"  -> Created filtered graph with {g_filtered.number_of_nodes()} nodes and {g_filtered.number_of_edges()} edges.")
    
    output_path = os.path.join(GEPHI_DIR, f"gephi_top_{TOP_N_EDGES}_edges_{date_str}.gexf")
    nx.write_gexf(g_filtered, output_path)
    print(f"  -> Saved to {output_path}")

print("\nGephi preparation complete.")