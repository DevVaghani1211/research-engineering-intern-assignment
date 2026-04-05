import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import umap
import logging

def cluster_results(df: pd.DataFrame, embeddings: np.ndarray, n_clusters: int = 5):
    """
    Cluster the retrieved dataframe using KMeans on the provided embeddings.
    Also reduces embedding dimensionality to 2D for visualization using UMAP.
    Extracts top keywords per cluster using TF-IDF.
    """
    if df.empty or len(df) < n_clusters:
        return df, pd.DataFrame()
        
    try:
        # Avoid crashing if sample size is extremely small
        n_clusters = min(n_clusters, len(df) // 2)
        n_clusters = max(n_clusters, 2)
        
        # 1. Dimensionality Reduction for UI
        # Adjust n_neighbors to be less than the dataset size
        n_neighbors = min(15, len(df) - 1)
        reducer = umap.UMAP(n_neighbors=n_neighbors, min_dist=0.1, n_components=2, random_state=42)
        u_embeds = reducer.fit_transform(embeddings)
        
        df['umap_x'] = u_embeds[:, 0]
        df['umap_y'] = u_embeds[:, 1]
        
        # 2. KMeans Clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
        cluster_labels = kmeans.fit_predict(embeddings)
        df['cluster'] = cluster_labels
        
        # 3. Extract Keywords using TF-IDF per cluster
        vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        tfidf_matrix = vectorizer.fit_transform(df['full_text'].tolist())
        feature_names = np.array(vectorizer.get_feature_names_out())
        
        cluster_info = []
        for i in range(n_clusters):
            # Get indices for this cluster
            cluster_idx = np.where(cluster_labels == i)[0]
            if len(cluster_idx) == 0:
                continue
                
            # Mean TF-IDF for the cluster
            mean_tfidf = np.asarray(tfidf_matrix[cluster_idx].mean(axis=0)).flatten()
            top_kw_idx = mean_tfidf.argsort()[-5:][::-1]
            top_keywords = feature_names[top_kw_idx]
            
            cluster_info.append({
                'cluster': i,
                'size': len(cluster_idx),
                'keywords': ", ".join(top_keywords)
            })
            
        cluster_df = pd.DataFrame(cluster_info)
        
        # Merge keyword labels into main df for plotting
        df['cluster_label'] = df['cluster'].apply(
            lambda c: cluster_df.loc[cluster_df['cluster'] == c, 'keywords'].values[0] if c in cluster_df['cluster'].values else f"Cluster {c}"
        )
        
        return df, cluster_df
        
    except Exception as e:
        logging.error(f"Clustering failed: {e}")
        df['umap_x'] = 0
        df['umap_y'] = 0
        df['cluster'] = -1
        df['cluster_label'] = 'Error'
        return df, pd.DataFrame()
