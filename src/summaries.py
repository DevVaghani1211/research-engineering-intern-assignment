import pandas as pd

def generate_time_series_summary(df: pd.DataFrame) -> str:
    """
    Deterministically generates a plain text summary describing the timeline 
    volume of a dataset, based on computed statistics.
    """
    if df.empty or 'date' not in df.columns:
        return "No time series data available to summarize."
        
    # Drop empty dates
    dates = pd.to_datetime(df['date'].dropna())
    if dates.empty:
        return "Not enough valid date records to summarize trends."
        
    counts = dates.value_counts(sort=False).sort_index()
    if counts.empty:
        return "No activity trends found."

    total_posts = counts.sum()
    peak_date = counts.idxmax()
    peak_volume = counts.max()
    
    # Calculate timespan
    date_range = (dates.max() - dates.min()).days
    
    # Calculate concentration (bursty vs sustained)
    # If standard dev is high relative to mean, it's bursty.
    mean_vol = counts.mean()
    std_vol = counts.std()
    
    is_bursty = std_vol > (mean_vol * 1.5)  # Threshold heuristic
    
    summary = f"A total of **{total_posts}** posts were analyzed over a **{max(date_range, 1)}-day** span. "
    
    if is_bursty and len(counts) > 2:
        summary += f"The narrative was highly **bursty**, concentrated tightly around a major spike on **{peak_date.strftime('%Y-%m-%d')}** with **{peak_volume}** posts. "
    elif len(counts) > 2:
        summary += f"The discussion showed a **sustained trend**, with a maximum peak on **{peak_date.strftime('%Y-%m-%d')}** ({peak_volume} posts). "
    else:
        summary += f"Activity appeared on only a few distinct days, peaking on **{peak_date.strftime('%Y-%m-%d')}**. "
        
    # Domain breakdown
    top_domains = df[df['domain'] != '']['domain'].value_counts()
    if not top_domains.empty:
        summary += f"The most amplified domain during this timeframe was **{top_domains.index[0]}**. "
        
    return summary

def generate_overall_investigation_summary(df: pd.DataFrame, query: str) -> str:
    """
    Generates a top-level narrative summary of the current investigation.
    """
    if df.empty:
        return "No results found for this query to summarize."
        
    top_sub = df['subreddit'].value_counts().index[0]
    avg_score = int(df['score'].mean())
    max_score = int(df['score'].max())
    
    auth_counts = df['author'].value_counts()
    repeat_authors = len(auth_counts[auth_counts > 1])
    
    summary = f"**Investigation Overview for \"{query}\":**\n\n"
    summary += f"Found **{len(df)}** highly relevant posts. "
    summary += f"The community driving the most discussion is **r/{top_sub}**. "
    summary += f"Engagement levels average at **{avg_score} points per post**, with the top post reaching **{max_score}**. "
    
    if repeat_authors > 0:
        summary += f"We identified **{repeat_authors}** actors posting multiple times, indicating deliberate amplification rather than purely organic scatter. "
        
    return summary
