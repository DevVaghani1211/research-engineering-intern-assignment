from pathlib import Path

# Base Paths (pathlib-based, repository-relative defaults)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Data Directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
ARTIFACTS_DIR = DATA_DIR / "artifacts"

# Specific File Paths
RAW_DATA_FILE = RAW_DATA_DIR / "data.jsonl"
PROCESSED_PARQUET_FILE = PROCESSED_DATA_DIR / "posts.parquet"
FAISS_INDEX_FILE = ARTIFACTS_DIR / "posts.faiss"
EMBEDDINGS_FILE = ARTIFACTS_DIR / "embeddings.npy"

# Model Configuration
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

# Assure directories exist
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
