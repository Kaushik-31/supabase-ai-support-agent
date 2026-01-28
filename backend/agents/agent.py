import chromadb
import boto3
import json
import os
from dotenv import load_dotenv

# Get project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

# ChromaDB client
chroma_client = chromadb.PersistentClient(path=os.path.join(PROJECT_ROOT, "chroma_db"))
collection = chroma_client.get_collection(name="supabase_knowledge_base")

# AWS Bedrock clients
bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.getenv('AWS_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)


def search_knowledge_base(query, n_results=3):
    """Search for relevant documents"""
    # Generate query embedding
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


def ask_agent(user_question):
    """Main agent function"""

    print(f"\n{'='*80}")
    print(f"Question: {user_question}")
    print(f"{'='*80}\n")

    # Step 1: Search knowledge base
    print("Searching knowledge base...")
    search_results = search_knowledge_base(user_question, n_results=3)

    # Step 2: Build context from search results
    context = ""
    for i, (doc, metadata) in enumerate(zip(search_results['documents'][0], search_results['metadatas'][0]), 1):
        context += f"\n--- Document {i} ({metadata['source']}: {metadata['filename']}) ---\n"
        context += doc[:1000]  # First 1000 chars of each doc
        context += "\n"

    print(f"Found {len(search_results['documents'][0])} relevant documents\n")

    # Step 3: Ask Claude to generate answer using context
    print("Generating answer with Claude...\n")

    system_prompt = """You are a helpful Supabase customer support agent.
Your job is to answer technical questions about Supabase using the documentation and GitHub issues provided.

Rules:
1. Answer based ONLY on the provided context
2. If the answer isn't in the context, say "I don't have that information in my knowledge base"
3. Be concise but helpful
4. Include code examples when relevant
5. Mention if the solution comes from a GitHub issue (shows it's a known problem)
"""

    user_prompt = f"""Question: {user_question}

Context from documentation and GitHub issues:
{context}

Please answer the question based on the context above."""

    # Call Claude
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "system": system_prompt
    })

    response = bedrock.invoke_model(
        modelId=os.getenv('BEDROCK_MODEL_ID'),
        body=body
    )

    response_body = json.loads(response['body'].read())
    answer = response_body['content'][0]['text']

    # Step 4: Display answer
    print(f"{'='*80}")
    print("Answer:")
    print(f"{'='*80}\n")
    print(answer)
    print(f"\n{'='*80}\n")

    return answer


# Test the agent
if __name__ == "__main__":

    # Test questions
    test_questions = [
        "How do I set up Google OAuth in Supabase?",
        "I'm getting a 502 error when logging in with Facebook. How do I fix it?",
        "How do I create a new table in my database?",
    ]

    for question in test_questions:
        ask_agent(question)
        print("\n" + "="*80 + "\n")
