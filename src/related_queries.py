import pandas as pd

def get_evidence_driven_queries(df: pd.DataFrame, cluster_df: pd.DataFrame, orig_query: str) -> list:
    """
    Generates sensible follow-up queries based on the actual result data 
    (Top domains, top subreddits, top clusters).
    """
    suggestions = []
    
    if df.empty:
        return ["Disinformation", "Bot network", "Propaganda"]
        
    # Suggestion 1: Dig into top domain
    domains = df[df['domain'] != '']['domain'].value_counts()
    if not domains.empty:
        top_dom = domains.index[0]
        if top_dom != 'reddit.com':
            suggestions.append(f"{orig_query} AND {top_dom}")
        else:
            if len(domains) > 1:
                suggestions.append(f"{orig_query} AND {domains.index[1]}")
            
    # Suggestion 2: Top keyword from the largest cluster
    if not cluster_df.empty:
        top_cluster_kws = cluster_df.iloc[0]['keywords'].split(", ")
        if len(top_cluster_kws) > 0:
            best_kw = top_cluster_kws[0]
            if best_kw.lower() not in orig_query.lower():
                suggestions.append(f"{orig_query} {best_kw}")
                
    # Suggestion 3: Top subreddit specific search
    subs = df['subreddit'].value_counts()
    if not subs.empty:
        suggestions.append(f"{orig_query} in r/{subs.index[0]}")
        
    # Fallback padding if we don't have 3
    fallbacks = ["narrative framing", "source validation", "deleted posts"]
    for fb in fallbacks:
        if len(suggestions) >= 3:
            break
        if fb not in suggestions:
            suggestions.append(fb)
            
    return suggestions[:3]
