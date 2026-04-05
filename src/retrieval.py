import logging
import numpy as np
import faiss
from src.data_loader import load_data, load_faiss_index, load_embedding_model

def search_posts(query: str, top_k: int = 100, min_score: int = None, subreddit: str = None, 
                 domain_filter: str = None, date_range: tuple = None):
    """
    Performs a semantic search against the FAISS index and applies metadata filters.
    Requires query to have content. If not, returns empty dataframe.
    """
    df = load_data()
    index = load_faiss_index()
    model = load_embedding_model()
    
    if df.empty or index is None or not query.strip():
        return pd.DataFrame() if df.empty else df.head(0)

    try:
        # Embed Query
        query_vector = model.encode([query], convert_to_numpy=True).astype('float32')
        faiss.normalize_L2(query_vector)

        # Retrieve a broad set of candidates before filtering to ensure we get enough
        # Get at least top_k * 5 to allow post-filtering
        search_k = min(len(df), max(top_k * 10, 500))
        distances, indices = index.search(query_vector, search_k)
        
        # Flatten
        distances = distances[0]
        indices = indices[0]
        
        # Build Results DataFrame
        results = df.iloc[indices].copy()
        results['similarity_score'] = distances

        # Optional light keyword blend (boost items that actually contain query terms)
        query_words = set(query.lower().split())
        if query_words:
            # simple occurrence boost
            def kw_boost(text):
                text_lower = str(text).lower()
                return sum(1 for w in query_words if w in text_lower) * 0.02
            
            results['similarity_score'] += results['full_text'].apply(kw_boost)
            results = results.sort_values('similarity_score', ascending=False)
        
        # Apply Filters
        if min_score is not None:
            results = results[results['score'] >= min_score]
            
        if subreddit and subreddit != "All":
            results = results[results['subreddit'] == subreddit]
            
        if domain_filter and domain_filter != "All":
            results = results[results['domain'] == domain_filter]
            
        if date_range and len(date_range) == 2:
            start_date, end_date = date_range
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            # Assuming 'date' is YYYY-MM-DD
            results = results[(results['date'] >= start_str) & (results['date'] <= end_str)]

        return results.head(top_k)

    except Exception as e:
        logging.error(f"Search failed: {e}")
        return df.head(0)
