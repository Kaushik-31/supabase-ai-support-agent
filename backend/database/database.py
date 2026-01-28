import psycopg2
import os
from dotenv import load_dotenv

# Get project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv(os.path.join(PROJECT_ROOT, '.env'))


def get_connection():
    """Create and return a database connection using DATABASE_URL"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables")
    return psycopg2.connect(database_url)


def init_database():
    """Create conversations table if it doesn't exist"""
    conn = get_connection()
    cursor = conn.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS conversations (
        id SERIAL PRIMARY KEY,
        session_id UUID NOT NULL,
        user_message TEXT NOT NULL,
        bot_response TEXT NOT NULL,
        intent VARCHAR(50),
        response_time_ms INTEGER,
        rating INTEGER,
        feedback_text TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_conversations_session_id
    ON conversations(session_id);

    CREATE INDEX IF NOT EXISTS idx_conversations_created_at
    ON conversations(created_at);
    """

    # Add columns if they don't exist (for existing databases)
    add_columns_query = """
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                       WHERE table_name='conversations' AND column_name='rating') THEN
            ALTER TABLE conversations ADD COLUMN rating INTEGER;
        END IF;
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                       WHERE table_name='conversations' AND column_name='feedback_text') THEN
            ALTER TABLE conversations ADD COLUMN feedback_text TEXT;
        END IF;
    END $$;
    """

    try:
        cursor.execute(create_table_query)
        cursor.execute(add_columns_query)
        conn.commit()
        print("Database initialized successfully")
    except Exception as e:
        conn.rollback()
        print(f"Error initializing database: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def save_feedback(conversation_id, rating, feedback_text=None):
    """Save user feedback for a conversation

    Args:
        conversation_id: The ID of the conversation to update
        rating: 1 for thumbs up, -1 for thumbs down
        feedback_text: Optional text comment from user
    """
    if rating not in (1, -1):
        raise ValueError("Rating must be 1 (thumbs up) or -1 (thumbs down)")

    conn = get_connection()
    cursor = conn.cursor()

    update_query = """
    UPDATE conversations
    SET rating = %s, feedback_text = %s
    WHERE id = %s
    RETURNING id;
    """

    try:
        cursor.execute(update_query, (rating, feedback_text, conversation_id))
        result = cursor.fetchone()
        conn.commit()
        if result:
            return result[0]
        return None
    except Exception as e:
        conn.rollback()
        print(f"Error saving feedback: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def save_conversation(session_id, user_msg, bot_response, intent, response_time):
    """Save a conversation to the database

    Args:
        session_id: UUID string for the session
        user_msg: The user's message
        bot_response: The bot's response
        intent: Classified intent (greeting, question, etc.)
        response_time: Response time in milliseconds
    """
    conn = get_connection()
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO conversations (session_id, user_message, bot_response, intent, response_time_ms)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id;
    """

    try:
        cursor.execute(insert_query, (session_id, user_msg, bot_response, intent, response_time))
        conversation_id = cursor.fetchone()[0]
        conn.commit()
        return conversation_id
    except Exception as e:
        conn.rollback()
        print(f"Error saving conversation: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    init_database()
