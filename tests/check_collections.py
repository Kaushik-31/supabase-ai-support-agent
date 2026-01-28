import chromadb
import os

# Get project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

chroma_client = chromadb.PersistentClient(path=os.path.join(PROJECT_ROOT, "chroma_db"))

collections = chroma_client.list_collections()

print("Collections in database:")
for col in collections:
    print(f"  - {col.name} ({col.count()} documents)")
