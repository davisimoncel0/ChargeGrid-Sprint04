import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.rag.vector_store import index_documents
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--size", type=int, default=800)
parser.add_argument("--overlap", type=int, default=120)
parser.add_argument("--collection", default="chargegrid_v1")
a = parser.parse_args()
print(index_documents(a.size, a.overlap, a.collection))
