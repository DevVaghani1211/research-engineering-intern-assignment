import logging
import sys
import numpy as np
import pandas as pd
from pathlib import Path

# Add project root to path so we can import src
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.config import (
    PROCESSED_PARQUET_FILE, 
    FAISS_INDEX_FILE, 
    EMBEDDING_MODEL_NAME, 
    EMBEDDING_DIM,
    EMBEDDINGS_FILE
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def build_artifacts():
    """
    Generate embeddings for processed data and create FAISS index.
    """
    try:
        from sentence_transformers import SentenceTransformer
        import faiss
    except ImportError:
        logging.error("Missing required libraries. Run: pip install sentence-transformers faiss-cpu")
        return

    if not PROCESSED_PARQUET_FILE.exists():
        logging.error(f"Processed file {PROCESSED_PARQUET_FILE} not found. Run preprocess.py first.")
        return

    logging.info("Loading processed dataset...")
    df = pd.read_parquet(PROCESSED_PARQUET_FILE)
    
    if df.empty:
        logging.error("Dataset is empty.")
        return
        
    texts = df['full_text'].tolist()
    logging.info(f"Loaded {len(texts)} texts for embedding.")

    logging.info(f"Loading embedding model '{EMBEDDING_MODEL_NAME}'...")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    
    logging.info("Encoding texts (this may take a while)...")
    # Using show_progress_bar=True if running interactively, though optional
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=64, convert_to_numpy=True)
    embeddings = np.array(embeddings).astype('float32')

    logging.info("Normalizing embeddings for cosine similarity search...")
    faiss.normalize_L2(embeddings)
    
    logging.info(f"Saving raw embeddings to {EMBEDDINGS_FILE}...")
    np.save(EMBEDDINGS_FILE, embeddings)

    logging.info(f"Building FAISS Index (Flat L2/Cosine) for dimension {EMBEDDING_DIM}...")
    # FlatIP + Normalized L2 distance = Cosine Similarity
    index = faiss.IndexFlatIP(EMBEDDING_DIM) 
    index.add(embeddings)
    
    logging.info(f"Writing index to {FAISS_INDEX_FILE}...")
    faiss.write_index(index, str(FAISS_INDEX_FILE))
    
    logging.info("Artifacts build complete!")

if __name__ == "__main__":
    build_artifacts()
