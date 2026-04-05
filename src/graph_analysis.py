import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import logging

def build_bipartite_graph(df: pd.DataFrame, max_nodes: int = 150):
    """
    Builds a bipartite network of Subreddit <-> Domain based on posts.
    Calculates PageRank centrality and returns Plotly figure + central nodes table.
    """
    if df.empty:
        return go.Figure(), pd.DataFrame()

    try:
        # Filter rows with domains
        graph_df = df[df['domain'].astype(bool) & (df['domain'] != '')].copy()
        
        if graph_df.empty:
            return go.Figure(), pd.DataFrame()

        # Aggregate edges
        edges = graph_df.groupby(['subreddit', 'domain']).size().reset_index(name='weight')
        
        # Build Graph
        G = nx.Graph()
        for _, row in edges.iterrows():
            sub = f"r/{row['subreddit']}"
            dom = row['domain']
            G.add_node(sub, bipartite=0, type='subreddit')
            G.add_node(dom, bipartite=1, type='domain')
            G.add_edge(sub, dom, weight=row['weight'])

        # Keep connected components
        if len(G.nodes) == 0:
            return go.Figure(), pd.DataFrame()

        # Prevent massive graphs
        if len(G.nodes) > max_nodes:
            # prune low degree nodes
            degrees = dict(G.degree())
            sorted_nodes = sorted(degrees.keys(), key=lambda x: degrees[x], reverse=True)
            keep_nodes = set(sorted_nodes[:max_nodes])
            G = G.subgraph(keep_nodes).copy()

        # Compute PageRank
        try:
            pagerank = nx.pagerank(G, weight='weight')
        except:
            pagerank = {n: 1.0 for n in G.nodes()}

        for n in G.nodes():
            G.nodes[n]['pagerank'] = pagerank[n]

        # Layout
        pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)

        # Plotly Traces
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )

        node_x = []
        node_y = []
        node_sizes = []
        node_colors = []
        hover_texts = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            pr_score = pagerank[node] * 5000
            size = max(10, min(pr_score, 50))
            node_sizes.append(size)
            
            is_sub = G.nodes[node]['type'] == 'subreddit'
            node_colors.append('#FF4500' if is_sub else '#1E90FF') # Orange for sub, Blue for domain
            
            node_type = "Subreddit" if is_sub else "Domain"
            hover_texts.append(f"{node_type}: {node}<br>Centrality: {pagerank[node]:.4f}")

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            hovertext=hover_texts,
            marker=dict(
                color=node_colors,
                size=node_sizes,
                line_width=2
            ))

        fig = go.Figure(data=[edge_trace, node_trace],
                     layout=go.Layout(
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0,l=0,r=0,t=0),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        plot_bgcolor='rgba(0,0,0,0)'
                     ))

        # Central nodes table
        central_nodes = pd.DataFrame(list(pagerank.items()), columns=['Node', 'PageRank'])
        central_nodes['Type'] = central_nodes['Node'].apply(lambda x: 'Subreddit' if x.startswith('r/') else 'Domain')
        central_nodes = central_nodes.sort_values('PageRank', ascending=False).head(10)

        return fig, central_nodes

    except Exception as e:
        logging.error(f"Graph analysis failed: {e}")
        return go.Figure(), pd.DataFrame()
