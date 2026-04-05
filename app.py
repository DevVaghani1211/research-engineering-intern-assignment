import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

from src.retrieval import search_posts
from src.clustering import cluster_results
from src.graph_analysis import build_bipartite_graph
from src.summaries import generate_time_series_summary, generate_overall_investigation_summary
from src.related_queries import get_evidence_driven_queries
from src.data_loader import load_data, load_embeddings

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Narrative Intelligence Dashboard", 
    page_icon="🔍", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enterprise technical theme for a serious research-tool feel
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    /* Force extremely dark slate background */
    .stApp {
        background-color: #0A0E17;
    }
    
    .reportview-container .main .block-container{
        padding-top: 2rem;
    }
    
    /* Serious Intelligence Title */
    .title-technical {
        font-family: 'JetBrains Mono', monospace;
        color: #E2E8F0;
        font-size: 2.2rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: -1px;
        border-left: 6px solid #00E5FF; /* Cyan Accent */
        padding-left: 15px;
        margin-bottom: 0;
    }
    
    /* Brutalist Metric Cards */
    .metric-card {
        background-color: #111827;
        padding: 20px;
        border: 1px solid #1F2937;
        border-top: 3px solid #3B82F6;
        transition: all 0.2s ease;
        margin-bottom: 10px;
    }
    .metric-card:hover {
        border-color: #00E5FF;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.1);
    }
    .metric-card h4 {
        color: #9CA3AF;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0;
    }
    .metric-card h2 {
        color: #F8FAFC;
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.5rem;
        margin-bottom: 0;
        font-weight: 700;
    }
    
    /* Technical Assistant Card */
    .assistant-card {
        background-color: #111827;
        padding: 24px;
        border: 1px solid #1F2937;
        border-left: 4px solid #F59E0B; /* Warning/Analysis Orange */
        margin-bottom: 25px;
        color: #D1D5DB;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    .assistant-card strong {
        color: #F8FAFC;
    }
    
    /* Sharp Buttons */
    .stButton>button {
        border-radius: 0px !important;
        border: 1px solid #1E293B !important;
        background-color: #0F172A !important;
        color: #60A5FA !important;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: rgba(59, 130, 246, 0.1) !important;
        color: #00E5FF !important;
        border-color: #00E5FF !important;
    }
    
    /* Sidebar styling overrides */
    section[data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid #1E293B;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Data Loading
# ---------------------------------------------------------
df_raw = load_data()
raw_embeds = load_embeddings()

if df_raw.empty:
    st.error("No processed data found. Please run `python scripts/preprocess.py` and `python scripts/build_artifacts.py` first.")
    st.stop()

# ---------------------------------------------------------
# Sidebar Filters
# ---------------------------------------------------------
st.sidebar.title("🔍 Investigation Filters")

# Subreddit filter
all_subs = ["All"] + sorted(df_raw['subreddit'].unique().tolist())
selected_sub = st.sidebar.selectbox("Subreddit", all_subs, index=0)

# Domain Filter
all_domains = ["All"] + sorted(df_raw[df_raw['domain'] != '']['domain'].unique().tolist())
selected_domain = st.sidebar.selectbox("Domain", all_domains, index=0)

# Score Filter
min_score = st.sidebar.slider("Minimum Score", 0, int(df_raw['score'].max()), 0)

# Date Filter
min_date = pd.to_datetime(df_raw['date'].min())
max_date = pd.to_datetime(df_raw['date'].max())
if pd.notnull(min_date) and pd.notnull(max_date):
    date_range = st.sidebar.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
else:
    date_range = None

# Cluster count setting
st.sidebar.markdown("---")
st.sidebar.subheader("Analytics Settings")
n_clusters = st.sidebar.slider("Number of Topic Clusters", 2, 10, 5)

# ---------------------------------------------------------
# Main UI
# ---------------------------------------------------------
st.markdown('<h1 class="title-technical">NARRATIVE INTELLIGENCE SYS.</h1>', unsafe_allow_html=True)
st.markdown("<p style='color: #9CA3AF; font-family: \"JetBrains Mono\", monospace; font-size: 0.85rem; margin-bottom: 2rem; margin-top: 10px;'>» MAPPING SUB-NARRATIVE TOPOLOGIES AND DOMAIN AMPLIFICATION VECTORS</p>", unsafe_allow_html=True)

# Search Bar
query = st.text_input("Enter a keyword, concept, or domain URL to begin investigation...", 
                     placeholder="e.g., 'climate legislation', 'election fraud claims', 'rt.com'")

if not query:
    # Initial empty load state
    st.info("👋 Welcome to the Narrative Intelligence Platform. Enter a search query above to start tracing a narrative.")
    st.stop()

# Ensure the query contains at least one letter or number (prevents only-punctuation inputs like "> < \ /")
import string
has_valid_chars = any(char.isalnum() for char in query)

if not query.strip() or not has_valid_chars:
    # They typed something, but it was just spaces or invalid punctuation
    st.warning("⚠️ The search query you entered is empty or invalid. Please type a meaningful keyword or concept.")
    st.stop()

# ---------------------------------------------------------
# Retrieve Results
# ---------------------------------------------------------
with st.spinner("Searching narrative vectors..."):
    results = search_posts(
        query=query, 
        top_k=200, 
        min_score=min_score,
        subreddit=selected_sub,
        domain_filter=selected_domain,
        date_range=date_range
    )

if results.empty:
    st.warning("No results found. Try broadening your query or relaxing your filters.")
    st.stop()

# Get the original indices to extract exact embeddings for clustering
result_indices = results.index.tolist()
result_embeds = raw_embeds[result_indices] if len(raw_embeds) > 0 else np.array([])

# ---------------------------------------------------------
# 1. Investigation Assistant (Summary)
# ---------------------------------------------------------
st.markdown("### 🤖 Investigation Assistant")
st.markdown(f'<div class="assistant-card">{generate_overall_investigation_summary(results, query)}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. Key Metrics
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.markdown(f'<div class="metric-card"><h4>Posts Found</h4><h2>{len(results)}</h2></div>', unsafe_allow_html=True)
col2.markdown(f'<div class="metric-card"><h4>Unique Subs</h4><h2>{results["subreddit"].nunique()}</h2></div>', unsafe_allow_html=True)
col3.markdown(f'<div class="metric-card"><h4>Unique Domains</h4><h2>{results[results["domain"] != ""]["domain"].nunique()}</h2></div>', unsafe_allow_html=True)
col4.markdown(f'<div class="metric-card"><h4>Avg Score</h4><h2>{int(results["score"].mean())}</h2></div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# Analytics Layout
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["📈 Timeline Map", "🧩 Topic Clusters", "🕸️ Subreddit-Domain Network", "📄 Post Explorer"])

# --- TAB 1: Timeline ---
with tab1:
    st.markdown("### Narrative Volume Over Time")
    
    if 'date' in results.columns and not results['date'].dropna().empty:
        time_counts = results.groupby('date').size().reset_index(name='count')
        time_counts['date'] = pd.to_datetime(time_counts['date'])
        
        fig_time = px.bar(time_counts, x='date', y='count', 
                         title='Daily Volume', 
                         color_discrete_sequence=['#FF6B6B'])
        fig_time.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_title="", 
            yaxis_title="Number of Posts",
            font=dict(family="Outfit", color="#E0E0E0"),
            hovermode="x unified"
        )
        st.plotly_chart(fig_time, use_container_width=True)
        
        st.markdown("**Timeline Summary:**")
        st.info(generate_time_series_summary(results))
    else:
        st.write("Not enough date information for timeline.")

# --- TAB 2: Clustering ---
with tab2:
    st.markdown("### Semantic Topic Clusters")
    with st.spinner("Extracting topics & reducing dimensions..."):
        cluster_res, cluster_df = cluster_results(results, result_embeds, n_clusters=n_clusters)
        
    if not cluster_df.empty:
        c1, c2 = st.columns([2, 1])
        
        with c1:
            fig_umap = px.scatter(
                cluster_res, x='umap_x', y='umap_y', color='cluster_label',
                hover_data=['title', 'subreddit', 'author'],
                title='UMAP Embedding Space (Colored by Topic)',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_umap.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Outfit", color="#E0E0E0"),
                legend=dict(
                    orientation="h", 
                    yanchor="top", 
                    y=-0.35, # Pushed further down to entirely clear the x-axis name
                    xanchor="center", 
                    x=0.5,
                    title=""
                ),
                margin=dict(b=200) # Increased padding to prevent clipping
            )
            fig_umap.update_traces(marker=dict(size=9, opacity=0.85, line=dict(width=0.5, color='white')))
            st.plotly_chart(fig_umap, use_container_width=True)
            
        with c2:
            st.markdown("#### Identified Topics")
            st.dataframe(cluster_df.rename(columns={'keywords': 'Distinguishing Terms', 'size': 'Post Count'})[['cluster', 'Post Count', 'Distinguishing Terms']], hide_index=True)
    else:
        st.write("Not enough data points to form reliable clusters.")

# --- TAB 3: Network Graph ---
with tab3:
    st.markdown("### Bipartite Amplifier Network (Subreddits vs. Domains)")
    st.markdown("This graph shows which subreddits are heavily relying on which external domains to push this narrative.")
    
    with st.spinner("Building network graph..."):
        fig_net, central_df = build_bipartite_graph(results)
        
    if not central_df.empty:
        nc1, nc2 = st.columns([2, 1])
        with nc1:
            st.plotly_chart(fig_net, use_container_width=True)
        with nc2:
            st.markdown("#### Most Central Actors (PageRank)")
            st.dataframe(central_df.rename(columns={'Node': 'Actor', 'PageRank': 'Centrality Score'})[['Actor', 'Type', 'Centrality Score']], hide_index=True)
    else:
        st.write("No external link domains found to build a network.")

# --- TAB 4: Post Explorer ---
with tab4:
    st.markdown("### Source Post Explorer")
    display_cols = ['subreddit', 'author', 'score', 'date', 'title', 'domain', 'permalink']
    avail_cols = [c for c in display_cols if c in results.columns]
    
    st.dataframe(
        results[avail_cols].sort_values('score', ascending=False),
        use_container_width=True,
        hide_index=True,
        column_config={
            "permalink": st.column_config.LinkColumn("Reddit Link")
        }
    )

# ---------------------------------------------------------
# Related Next Steps
# ---------------------------------------------------------
st.markdown("---")
st.subheader("💡 Suggested Next Investigations")

cluster_info_df = cluster_df if 'cluster_df' in locals() else pd.DataFrame()
suggestions = get_evidence_driven_queries(results, cluster_info_df, query)

s_cols = st.columns(len(suggestions))
for idx, sug in enumerate(suggestions):
    s_cols[idx].button(f"🔍 {sug}", key=f"sug_{idx}", disabled=True, help="Copy this query to continue investigating.")
