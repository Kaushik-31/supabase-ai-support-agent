"""
One-time setup script for the Supabase Support Agent.
Run this before starting the app to initialize the database.
"""
import uuid
from backend.database.database import init_database, save_conversation


def create_sample_conversations():
    """Create 3 sample conversations for testing"""
    samples = [
        {
            "session_id": str(uuid.uuid4()),
            "user_msg": "How do I set up authentication in Supabase?",
            "bot_response": "To set up authentication in Supabase, go to your project dashboard, click on 'Authentication' in the sidebar, then enable the providers you want (Email, Google, GitHub, etc.). You can configure each provider's settings and customize email templates.",
            "intent": "question",
            "response_time": 450
        },
        {
            "session_id": str(uuid.uuid4()),
            "user_msg": "What is Row Level Security?",
            "bot_response": "Row Level Security (RLS) in Supabase allows you to control which rows users can access in your database tables. You create policies that define conditions for SELECT, INSERT, UPDATE, and DELETE operations. Enable RLS on a table and add policies to secure your data at the database level.",
            "intent": "question",
            "response_time": 380
        },
        {
            "session_id": str(uuid.uuid4()),
            "user_msg": "Hello!",
            "bot_response": "Hello! I'm your Supabase support agent. How can I help you today?",
            "intent": "greeting",
            "response_time": 50
        }
    ]

    for sample in samples:
        conversation_id = save_conversation(
            sample["session_id"],
            sample["user_msg"],
            sample["bot_response"],
            sample["intent"],
            sample["response_time"]
        )
        print(f"Created sample conversation {conversation_id}: {sample['intent']}")


if __name__ == "__main__":
    print("Initializing database...")
    init_database()
    print()
    print("Creating sample conversations...")
    create_sample_conversations()
    print()
    print("Setup complete! You can now run the app with: python app.py")
