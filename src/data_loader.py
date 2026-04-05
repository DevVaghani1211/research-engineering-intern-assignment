import streamlit as st
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from src.config import (
    PROCESSED_PARQUET_FILE, 
    FAISS_INDEX_FILE, 
    EMBEDDINGS_FILE,
    EMBEDDING_MODEL_NAME
)

@st.cache_data(show_spinner="Loading data...")
def load_data():
    """Load the preprocessed pandas DataFrame."""
    if not PROCESSED_PARQUET_FILE.exists():
        return pd.DataFrame()
    return pd.read_parquet(PROCESSED_PARQUET_FILE)

@st.cache_resource(show_spinner="Loading FAISS Index...")
def load_faiss_index():
    """Load FAISS index."""
    if not FAISS_INDEX_FILE.exists():
        return None
    return faiss.read_index(str(FAISS_INDEX_FILE))

@st.cache_resource(show_spinner="Loading Embedding Model...")
def load_embedding_model():
    """Load the SentenceTransformer model."""
    return SentenceTransformer(EMBEDDING_MODEL_NAME)

@st.cache_data(show_spinner="Loading Raw Embeddings...")
def load_embeddings():
    """Load the raw numpy embeddings for clustering or visualization."""
    if not EMBEDDINGS_FILE.exists():
        return np.array([])
    return np.load(EMBEDDINGS_FILE)
