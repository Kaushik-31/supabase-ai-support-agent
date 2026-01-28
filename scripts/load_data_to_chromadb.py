import os
import json
import boto3
from dotenv import load_dotenv
import chromadb
import time

# Get project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

# AWS Bedrock client
bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.getenv('AWS_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

# ChromaDB client
chroma_client = chromadb.PersistentClient(path=os.path.join(PROJECT_ROOT, "chroma_db"))

# Create or get collection
collection = chroma_client.get_or_create_collection(
    name="supabase_knowledge_base",
    metadata={"description": "Supabase docs and GitHub issues with embeddings"}
)


def generate_embedding(text):
    """Generate embedding using AWS Bedrock Titan"""
    try:
        # Use Titan Embeddings model
        body = json.dumps({
            "inputText": text[:8000]  # Titan limit is ~8K chars
        })

        response = bedrock.invoke_model(
            modelId='amazon.titan-embed-text-v1',
            body=body
        )

        response_body = json.loads(response['body'].read())
        embedding = response_body['embedding']

        return embedding

    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None


def load_documents():
    """Load all documents from data/raw and add to ChromaDB"""

    print("Starting to load documents into ChromaDB...")
    print("="*80)

    documents = []
    metadatas = []
    ids = []
    embeddings = []

    # Load documentation files
    docs_path = os.path.join(PROJECT_ROOT, "data", "raw")
    if os.path.exists(docs_path):
        for filename in os.listdir(docs_path):
            if filename.endswith('.txt'):
                filepath = os.path.join(docs_path, filename)

                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Generate embedding
                print(f"Processing: {filename}")
                embedding = generate_embedding(content)

                if embedding:
                    documents.append(content)
                    metadatas.append({
                        'source': 'documentation',
                        'filename': filename
                    })
                    ids.append(f"doc_{filename}")
                    embeddings.append(embedding)
                    print(f"  Added to collection")

                # Be nice to API - wait between requests
                time.sleep(1)

    # Load GitHub issues
    github_path = os.path.join(PROJECT_ROOT, "data", "raw", "github")
    if os.path.exists(github_path):
        for filename in os.listdir(github_path):
            if filename.endswith('.txt'):
                filepath = os.path.join(github_path, filename)

                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Generate embedding
                print(f"Processing: {filename}")
                embedding = generate_embedding(content)

                if embedding:
                    documents.append(content)
                    metadatas.append({
                        'source': 'github_issue',
                        'filename': filename
                    })
                    ids.append(f"github_{filename}")
                    embeddings.append(embedding)
                    print(f"  Added to collection")

                # Be nice to API
                time.sleep(1)

    # Add all documents to ChromaDB
    if documents:
        print(f"\n{'='*80}")
        print(f"Adding {len(documents)} documents to ChromaDB...")

        collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

        print(f"Successfully loaded {len(documents)} documents!")
        print(f"Collection now has {collection.count()} total documents")

    return len(documents)


if __name__ == "__main__":
    count = load_documents()
    print(f"\nDone! Loaded {count} documents with embeddings into ChromaDB")
