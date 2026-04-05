import json
import logging
import pandas as pd
import sys
from pathlib import Path

# Add project root to path so we can import src
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.config import RAW_DATA_FILE, PROCESSED_PARQUET_FILE
from src.utils import parse_date_robust, clean_text

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def preprocess_data():
    """
    Reads raw JSONL file, extracts and cleans relevant fields, Handles missing keys, 
    and outputs a optimized Parquet file.
    """
    if not RAW_DATA_FILE.exists():
        logging.error(f"Raw data file not found at {RAW_DATA_FILE}")
        return

    logging.info(f"Loading raw data from {RAW_DATA_FILE}...")
    records = []
    
    with open(RAW_DATA_FILE, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f):
            if not line.strip():
                continue
            try:
                raw_obj = json.loads(line)
            except json.JSONDecodeError:
                logging.warning(f"Failed to decode JSON on line {idx + 1}")
                continue
                
            # We only care about t3 (Link/Post) objects based on dataset structure
            if raw_obj.get('kind') != 't3':
                continue
                
            data = raw_obj.get('data', {})
            if not data:
                continue
                
            post_id = data.get('id', '')
            title = clean_text(data.get('title', ''))
            selftext = clean_text(data.get('selftext', ''))
            
            # Construct full text for embedding
            full_text = f"{title}\n\n{selftext}".strip()
            
            # Avoid totally empty posts
            if not full_text:
                continue
                
            author = data.get('author', '[deleted]')
            subreddit = data.get('subreddit', 'unknown')
            
            # Parse Dates
            created_utc = data.get('created_utc')
            dt = parse_date_robust(created_utc)
            
            date_str, week_str, month_str = None, None, None
            if dt:
                date_str = dt.strftime('%Y-%m-%d')
                week_str = dt.strftime('%Y-%W')
                month_str = dt.strftime('%Y-%m')
                
            url = data.get('url', '')
            domain = data.get('domain', '')
            
            # Sometimes self.subreddit is domain for text posts. Clean it up if needed.
            if domain.startswith('self.'):
                domain = 'reddit.com'
                
            score = data.get('score', 0)
            num_comments = data.get('num_comments', 0)
            upvote_ratio = data.get('upvote_ratio', 0.0)
            permalink = data.get('permalink', '')
            crosspost_parent = data.get('crosspost_parent', '')
            text_length = len(full_text)
            
            records.append({
                'post_id': post_id,
                'title': title,
                'selftext': selftext,
                'full_text': full_text,
                'author': author,
                'subreddit': subreddit,
                'created_utc': created_utc,
                'datetime': dt,
                'date': date_str,
                'week': week_str,
                'month': month_str,
                'url': url,
                'domain': domain,
                'score': score,
                'num_comments': num_comments,
                'upvote_ratio': upvote_ratio,
                'permalink': permalink,
                'crosspost_parent': crosspost_parent,
                'text_length': text_length
            })

    logging.info(f"Loaded {len(records)} valid posts.")
    
    if not records:
        logging.warning("No records to save.")
        return
        
    df = pd.DataFrame(records)
    
    # Handle missing values broadly to prevent issues down the line
    df['title'] = df['title'].fillna('')
    df['selftext'] = df['selftext'].fillna('')
    df['full_text'] = df['full_text'].fillna('')
    df['author'] = df['author'].fillna('[deleted]')
    df['subreddit'] = df['subreddit'].fillna('unknown')
    df['domain'] = df['domain'].fillna('')
    df['score'] = pd.to_numeric(df['score'], errors='coerce').fillna(0)
    
    logging.info(f"Saving processed data to {PROCESSED_PARQUET_FILE}...")
    df.to_parquet(PROCESSED_PARQUET_FILE, index=False)
    logging.info("Preprocessing complete.")

if __name__ == "__main__":
    preprocess_data()
