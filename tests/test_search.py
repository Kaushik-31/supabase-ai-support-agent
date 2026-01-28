import chromadb
import boto3
import json
import os
import sys
from dotenv import load_dotenv

# Get project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

# Connect to ChromaDB
client = chromadb.PersistentClient(path=os.path.join(PROJECT_ROOT, "chroma_db"))

collection = client.get_collection(name="supabase_knowledge_base")

# Bedrock for generating query embeddings
bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.getenv('AWS_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)


def search_knowledge_base(query, n_results=3):
    """Search the knowledge base"""

    # Generate embedding for the query
    body = json.dumps({"inputText": query})
    response = bedrock.invoke_model(
        modelId='amazon.titan-embed-text-v1',
        body=body
    )
    query_embedding = json.loads(response['body'].read())['embedding']

    # Search ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return results


# Test queries
test_queries = [
    "How do I set up Google authentication?",
    "I'm getting a 502 error",
    "How to create a database table?",
]

if __name__ == "__main__":
    print("Testing Knowledge Base Search")
    print("="*80)

    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-"*80)

        results = search_knowledge_base(query, n_results=2)

        for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
            print(f"\nResult {i}:")
            print(f"   Source: {metadata['source']}")
            print(f"   File: {metadata['filename']}")
            print(f"   Preview: {doc[:200]}...")
            print()

    print("="*80)
    print("Search is working! Your knowledge base is ready!")
