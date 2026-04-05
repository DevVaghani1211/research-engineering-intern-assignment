# Narrative Intelligence Dashboard for Reddit

## Project Overview
The **Narrative Intelligence Dashboard** is an investigative OSINT tool designed for researchers, journalists, and policy analysts. This application goes beyond standard keyword searching by leveraging a sophisticated **semantic search engine** and **unsupervised learning algorithms** to trace how narratives, links, and specific concepts spread across Reddit communities.

Unlike a generic business analytics dashboard, this tool is built entirely around an investigative workflow:
1. Search via concept (semantic embedding).
2. Trace the narrative timeline to identify bursty vs. sustained campaigns.
3. Automatically cluster results into thematic topics using KMeans + TF-IDF labeling.
4. Visualize relationships between Subreddits and Domains via PageRank network centrality.

## Architecture

```text
reddit-narrative-dashboard/
  ├── app.py                     # Streamlit frontend entry point
  ├── requirements.txt           # Deployment dependencies
  ├── README.md                  # Project documentation
  ├── data/                      
  │   ├── raw/data.jsonl         # Original raw dataset
  │   ├── processed/             # Cleaned Parquet exports
  │   └── artifacts/             # FAISS index and numpy embeddings
  ├── scripts/
  │   ├── preprocess.py          # Data ingestion and flattening
  │   └── build_artifacts.py     # Embedding generation and index creation
  └── src/
      ├── config.py              # Pathlib-based configuration
      ├── data_loader.py         # App caching integration
      ├── retrieval.py           # FAISS semantic search logic
      ├── clustering.py          # UMAP + KMeans + TF-IDF clusterer
      ├── graph_analysis.py      # NetworkX bipartite graph & PageRank
      ├── summaries.py           # Deterministic NLP timeline summaries
      ├── related_queries.py     # Evidence-driven query suggester
      └── utils.py               # Robust parsing and helpers
```

## Setup & Local Installation

1. **Clone the repository and prepare the data**
Make sure your raw Reddit JSONL data is placed in `data/raw/data.jsonl`.

2. **Create a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the Data Pipeline**
Extracts nested JSON fields, cleans data, and saves to an optimized Parquet format.
```bash
python scripts/preprocess.py
```

5. **Build AI Artifacts**
Embeds text and builds the FAISS vector index. (This step downloads the `all-MiniLM-L6-v2` model and may take a few minutes depending on dataset size).
```bash
python scripts/build_artifacts.py
```

6. **Start the Dashboard**
```bash
streamlit run app.py
```

## How to Deploy (Streamlit Community Cloud / Render)

1. Ensure the generated artifact files (`posts.parquet`, `posts.faiss`, `embeddings.npy`) are securely stored. For cloud deployment, you should either upload these artifacts to your host or configure an S3 bucket in `src/config.py` to pull them down, since large indices aren't suitable for Git.
2. Push the codebase to GitHub.
3. Connect the repo to Streamlit Community Cloud or Render.
4. Set the build command to `pip install -r requirements.txt` and the start command to `streamlit run app.py`.

## Machine Learning & AI Components

- **Semantic Search:** `sentence-transformers/all-MiniLM-L6-v2` mapped to a robust CPU `FAISS` index.
- **Topic Clustering:** `KMeans` used dynamically based on the searched subset. `umap-learn` handles 2D projection for the interactive UI graph.
- **Cluster Labeling:** `scikit-learn`'s `TfidfVectorizer` identifies discriminating keywords per cluster.
- **Network Centrality:** `NetworkX` calculates `PageRank` on a bipartite Subreddit-Domain graph to locate high-leverage nodes driving external references.

## Design Decisions & Trade-offs

- **Parquet over DB:** Parquet allows fast column reading and avoids the overhead of setting up a PostgreSQL instance, ensuring the application remains simple to deploy.
- **Deterministic Summaries vs LLMs:** Instead of risking hallucinations or long API wait times/costs for LLM calls, the "Investigation Assistant" uses statistical rules (burst volume, standard deviations) to formulate narrative text.
- **FAISS vs VDB:** A local FAISS index avoids external SaaS dependencies, making it cheap and entirely self-contained. 

## Semantic Search Examples 
(Where keyword matching would typically fail, but semantic search succeeds)
1. *Query:* `"eco-friendly transport"` 
   *Finds:* "biking to work", "new EV battery tech", "reducing emissions"
2. *Query:* `"wealth inequality"`
   *Finds:* "billionaire tax loopholes", "housing market pricing out locals", "wage stagnation"
3. *Query:* `"misinformation networks"`
   *Finds:* "fake news bots", "propaganda botfarms", "manipulated media spread"