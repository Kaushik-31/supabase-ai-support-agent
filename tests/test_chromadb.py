import chromadb
import os

# Get project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Create ChromaDB client (using current API)
client = chromadb.PersistentClient(path=os.path.join(PROJECT_ROOT, "chroma_db"))

# Create a collection for our knowledge base
collection = client.get_or_create_collection(
    name="supabase_docs",
    metadata={"description": "Supabase documentation and GitHub issues"}
)

# Test adding a document
collection.add(
    documents=["This is a test document about Supabase authentication"],
    ids=["test_1"],
    metadatas=[{"source": "test"}]
)

# Test searching
results = collection.query(
    query_texts=["authentication"],
    n_results=1
)

print("ChromaDB is working!")
print(f"Found document: {results['documents'][0]}")
print(f"Vector database created at: {os.path.join(PROJECT_ROOT, 'chroma_db')}")
