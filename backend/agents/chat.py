import chromadb
import boto3
import json
import os
import uuid
import time
from dotenv import load_dotenv
from backend.database.database import save_conversation

# Get project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

# ChromaDB client
chroma_client = chromadb.PersistentClient(path=os.path.join(PROJECT_ROOT, "chroma_db"))
collection = chroma_client.get_collection(name="supabase_knowledge_base")

# AWS Bedrock client
bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.getenv('AWS_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

# Session-isolated conversation histories
active_sessions = {}


def search_knowledge_base(query, n_results=3):
    """Search for relevant documents"""
    body = json.dumps({"inputText": query})
    response = bedrock.invoke_model(
        modelId='amazon.titan-embed-text-v1',
        body=body
    )
    query_embedding = json.loads(response['body'].read())['embedding']

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return results


def check_conversation_has_supabase_context(history):
    """Check if recent conversation history contains Supabase-related content"""
    supabase_keywords = [
        'supabase', 'database', 'postgres', 'sql', 'table', 'column',
        'auth', 'authentication', 'login', 'signup', 'user', 'password',
        'storage', 'bucket', 'upload', 'download', 'file',
        'api', 'rest', 'client', 'sdk', 'javascript', 'react', 'next',
        'realtime', 'subscription', 'websocket', 'broadcast',
        'rls', 'row level security', 'policy', 'permission',
        'query', 'insert', 'update', 'delete', 'select',
        'oauth', 'google', 'facebook', 'github', 'social login',
        'error', 'cors', 'jwt', 'token', 'session', 'deploy', 'hosting'
    ]

    # Check last 6 messages for Supabase context
    recent = history[-6:] if len(history) > 6 else history
    for msg in recent:
        content = msg.get('content', '').lower()
        if any(keyword in content for keyword in supabase_keywords):
            return True
    return False


def classify_intent(message, history=None):
    """Classify user intent using priority-based pattern matching

    Priority system (highest wins):
    1. Has Supabase keywords → 'question'
    2. Has entertainment/general knowledge → 'off_topic'
    3. Has greeting (short message, no prior context) → 'greeting'
    4. Has thanks/praise → 'thanks' or 'praise'
    5. Default based on context

    Args:
        message: The user's message
        history: Optional conversation history for context awareness
    """
    message_lower = message.lower().strip()
    history = history or []
    words = message_lower.split()

    # Check if conversation already has Supabase context
    has_prior_context = check_conversation_has_supabase_context(history)

    # === Early exits for invalid input ===
    if not message or len(message.strip()) < 2:
        return 'unclear'

    if not any(c.isalpha() for c in message):
        return 'unclear'

    # === Detect ALL pattern types (don't return yet) ===

    # Supabase/tech keywords
    supabase_keywords = [
        'supabase', 'database', 'postgres', 'sql', 'table', 'column',
        'auth', 'authentication', 'login', 'signup', 'password',
        'storage', 'bucket', 'upload', 'download',
        'api', 'rest', 'client', 'sdk', 'javascript', 'react', 'next',
        'realtime', 'subscription', 'websocket', 'broadcast',
        'rls', 'row level security', 'policy', 'permission',
        'query', 'insert', 'update', 'delete', 'select',
        'oauth', 'social login',
        'error', '502', '500', '401', '403', '404', 'cors',
        'jwt', 'token', 'session', 'deploy', 'hosting'
    ]
    has_supabase = any(keyword in message_lower for keyword in supabase_keywords)

    # Entertainment/Personal
    entertainment = [
        'joke', 'funny', 'laugh', 'story', 'sing', 'song',
        'movie', 'music', 'game', 'play', 'favorite color',
        'hobby', 'dream', 'feel', 'emotion', 'tell me about yourself',
        'tell me about urself', 'about yourself', 'about you',
        'who are you', 'what are you', 'are you human', 'are you robot',
        'how old are you', 'where are you from', 'who created you',
        'who made you', 'who built you'
    ]
    has_entertainment = any(keyword in message_lower for keyword in entertainment)

    # Personal questions that should ALWAYS be off_topic (checked before Supabase keywords)
    personal_questions = [
        'tell me about yourself', 'tell me about urself', 'about yourself',
        'who are you', 'what are you', 'who made you', 'who built you',
        'who created you', 'are you human', 'are you robot', 'are you ai',
        'how old are you', 'where are you from'
    ]
    is_personal_question = any(pattern in message_lower for pattern in personal_questions)

    # General Knowledge
    general_knowledge = [
        'weather', 'time', 'date', 'president', 'news', 'celebrity',
        'cook', 'recipe', 'capital', 'mountain', 'ocean', 'country',
        'sport', 'team', 'win', 'lose', 'score',
        'stock', 'invest', 'bitcoin', 'crypto', 'exchange rate',
        'lose weight', 'diet', 'exercise', 'health', 'doctor',
        'meaning of life', 'philosophy', 'religion', 'politics'
    ]
    has_general_knowledge = any(keyword in message_lower for keyword in general_knowledge)

    # Non-Supabase tech
    non_supabase_tech = [
        'mongodb', 'mysql', 'firebase', 'aws', 'azure', 'docker',
        'kubernetes', 'redis', 'graphql', 'prisma', 'django'
    ]
    has_other_tech = any(tech in message_lower for tech in non_supabase_tech)

    # Greetings
    greetings = [
        'hi', 'hello', 'hey', 'greetings', 'good morning',
        'good afternoon', 'good evening', 'howdy', 'yo', 'sup'
    ]
    has_greeting = (
        (len(words) > 0 and words[0] in greetings) or
        message_lower in greetings
    )

    # Thanks/Goodbye
    thanks_patterns = [
        'thank', 'thx', 'appreciate', "that's it", "thats it",
        'perfect', 'got it', 'understood', 'bye', 'goodbye',
        'see you', 'later', 'have a good', 'take care'
    ]
    has_thanks = any(pattern in message_lower for pattern in thanks_patterns)

    # Praise/Compliments
    praise_keywords = [
        'amazing', 'awesome', 'great job', 'helpful', 'impressive',
        'smart', 'clever', 'brilliant', 'inspiration', 'best',
        'perfect answer', 'exactly what', 'you rock'
    ]
    has_praise = any(keyword in message_lower for keyword in praise_keywords)

    # Follow-up patterns
    followup_patterns = [
        'yes', 'no', 'ok', 'okay', 'sure', 'right', 'correct',
        'what about', 'how about', 'and', 'also', 'but', 'however',
        'can you', 'could you', 'would you', 'please', 'show me',
        'explain', 'tell me', 'what if', 'why', 'when', 'where',
        'how do i', 'how can i', 'what is', 'is it', 'does it',
        'another', 'more', 'else', 'instead', 'different', 'other'
    ]
    has_followup = any(pattern in message_lower for pattern in followup_patterns)

    # === Apply priority rules ===

    # Priority 0: Personal questions ALWAYS off_topic (before Supabase check)
    if is_personal_question:
        return 'off_topic'

    # Priority 1: Supabase keywords ALWAYS win
    if has_supabase:
        return 'question'

    # Priority 2: Off-topic (entertainment, general knowledge, other tech)
    if has_entertainment or has_general_knowledge:
        return 'off_topic'

    if has_other_tech and not has_prior_context:
        return 'off_topic'

    # Priority 3: Greeting (only if short and no prior context)
    if has_greeting and len(words) < 5 and not has_prior_context:
        return 'greeting'

    # Priority 4: Thanks/Praise (only if not asking a question)
    if has_thanks and '?' not in message and 'how' not in message_lower:
        return 'thanks'

    if has_praise and '?' not in message:
        return 'praise'

    # Priority 5: Context-based defaults

    # Follow-up in ongoing conversation
    if has_prior_context and (has_followup or '?' in message):
        return 'question'

    # Has prior context, treat as continuation
    if has_prior_context:
        return 'question'

    # Vague messages without context
    vague_only = message_lower in [
        'help', 'error', 'problem', 'issue', 'broken', 'not working',
        'stuck', 'confused', 'urgent', 'please help'
    ]
    if vague_only:
        return 'unclear'

    # Question mark but no relevant context
    if '?' in message:
        return 'off_topic'

    # Very short messages without context
    if len(words) < 4:
        return 'unclear'

    # Default: unclear
    return 'unclear'


def chat(user_message, session_id=None):
    """Chat with the agent

    Args:
        user_message: The user's message
        session_id: UUID string for the session (generated if not provided)

    Returns:
        dict with 'answer' and 'conversation_id' keys
    """
    start_time = time.time()

    # Generate session_id if not provided
    if session_id is None:
        session_id = str(uuid.uuid4())

    # Get session-specific history
    current_history = active_sessions.get(session_id, [])

    # Classify intent with conversation context
    intent = classify_intent(user_message, current_history)

    # Handle non-question intents
    if intent == 'greeting':
        answer = "Hello! I'm your Supabase support agent. How can I help you today?"
        current_history.append({"role": "user", "content": user_message})
        current_history.append({"role": "assistant", "content": answer})
        active_sessions[session_id] = current_history
        response_time_ms = int((time.time() - start_time) * 1000)
        conversation_id = save_conversation(session_id, user_message, answer, intent, response_time_ms)
        return {"answer": answer, "conversation_id": conversation_id}

    elif intent == 'thanks':
        answer = "You're welcome! Feel free to ask if you have any other questions about Supabase."
        current_history.append({"role": "user", "content": user_message})
        current_history.append({"role": "assistant", "content": answer})
        active_sessions[session_id] = current_history
        response_time_ms = int((time.time() - start_time) * 1000)
        conversation_id = save_conversation(session_id, user_message, answer, intent, response_time_ms)
        return {"answer": answer, "conversation_id": conversation_id}

    elif intent == 'praise':
        answer = "Thank you for the kind words! I'm here to help with any Supabase questions you have. What would you like to know?"
        current_history.append({"role": "user", "content": user_message})
        current_history.append({"role": "assistant", "content": answer})
        active_sessions[session_id] = current_history
        response_time_ms = int((time.time() - start_time) * 1000)
        conversation_id = save_conversation(session_id, user_message, answer, intent, response_time_ms)
        return {"answer": answer, "conversation_id": conversation_id}

    elif intent == 'unclear':
        answer = "I'm not sure I understand. Could you please ask a more specific question about Supabase? For example, you can ask about authentication, database, storage, API, or troubleshooting."
        current_history.append({"role": "user", "content": user_message})
        current_history.append({"role": "assistant", "content": answer})
        active_sessions[session_id] = current_history
        response_time_ms = int((time.time() - start_time) * 1000)
        conversation_id = save_conversation(session_id, user_message, answer, intent, response_time_ms)
        return {"answer": answer, "conversation_id": conversation_id}

    elif intent == 'off_topic':
        answer = "I'm a Supabase support agent and can only help with questions about Supabase (database, authentication, storage, API, realtime, etc.). Do you have any questions about Supabase?"
        current_history.append({"role": "user", "content": user_message})
        current_history.append({"role": "assistant", "content": answer})
        active_sessions[session_id] = current_history
        response_time_ms = int((time.time() - start_time) * 1000)
        conversation_id = save_conversation(session_id, user_message, answer, intent, response_time_ms)
        return {"answer": answer, "conversation_id": conversation_id}

    # Hallucination prevention - detect questions we can't answer reliably
    message_lower = user_message.lower()

    # Check for pricing questions
    pricing_keywords = ['cost', 'price', 'pricing', 'how much', 'expensive', 'pay', 'subscription', 'plan']
    if any(keyword in message_lower for keyword in pricing_keywords):
        answer = "I don't have pricing information. Please check https://supabase.com/pricing for current plans and costs."
        current_history.append({"role": "user", "content": user_message})
        current_history.append({"role": "assistant", "content": answer})
        active_sessions[session_id] = current_history
        response_time_ms = int((time.time() - start_time) * 1000)
        conversation_id = save_conversation(session_id, user_message, answer, 'pricing', response_time_ms)
        return {"answer": answer, "conversation_id": conversation_id}

    # Check for unsupported deployment platforms (without 'supabase' context)
    unsupported_platforms = ['azure', 'heroku', 'digital ocean', 'digitalocean', 'render']
    has_unsupported = None
    for platform in unsupported_platforms:
        if platform in message_lower and 'supabase' not in message_lower:
            has_unsupported = platform
            break
    if has_unsupported:
        answer = f"I don't have deployment information for {has_unsupported}. My knowledge covers Supabase-specific deployment and configuration."
        current_history.append({"role": "user", "content": user_message})
        current_history.append({"role": "assistant", "content": answer})
        active_sessions[session_id] = current_history
        response_time_ms = int((time.time() - start_time) * 1000)
        conversation_id = save_conversation(session_id, user_message, answer, 'unsupported', response_time_ms)
        return {"answer": answer, "conversation_id": conversation_id}

    # Check for roadmap/future feature questions
    roadmap_keywords = ['when will', 'roadmap', 'future', 'upcoming', 'release', 'next version']
    if any(keyword in message_lower for keyword in roadmap_keywords):
        answer = "I don't have roadmap information. Please check the official Supabase GitHub (https://github.com/supabase/supabase) or blog (https://supabase.com/blog) for announcements."
        current_history.append({"role": "user", "content": user_message})
        current_history.append({"role": "assistant", "content": answer})
        active_sessions[session_id] = current_history
        response_time_ms = int((time.time() - start_time) * 1000)
        conversation_id = save_conversation(session_id, user_message, answer, 'roadmap', response_time_ms)
        return {"answer": answer, "conversation_id": conversation_id}

    # Vague question detection - ask for clarification
    vague_exact = ['help', 'error', 'not working', "it's not working", 'broken', 'issue', 'problem']
    is_vague_exact = message_lower.strip() in vague_exact

    # Check for short messages without Supabase keywords
    supabase_check = ['supabase', 'database', 'auth', 'storage', 'api', 'table', 'query', 'rls', 'realtime']
    has_supabase_keyword = any(kw in message_lower for kw in supabase_check)
    words = message_lower.split()
    is_short_vague = len(words) < 3 and not has_supabase_keyword

    # Check for strong prior context (last 2 messages)
    recent_context = current_history[-2:] if len(current_history) >= 2 else current_history
    has_strong_context = any(
        any(kw in msg.get('content', '').lower() for kw in supabase_check)
        for msg in recent_context
    )

    if (is_vague_exact or is_short_vague) and not has_strong_context:
        answer = "I'd be happy to help! Can you tell me more specifically what you're trying to do or what error you're seeing? For example, are you having issues with authentication, database, storage, or something else?"
        current_history.append({"role": "user", "content": user_message})
        current_history.append({"role": "assistant", "content": answer})
        active_sessions[session_id] = current_history
        response_time_ms = int((time.time() - start_time) * 1000)
        conversation_id = save_conversation(session_id, user_message, answer, 'vague', response_time_ms)
        return {"answer": answer, "conversation_id": conversation_id}

    # For real questions, search knowledge base
    try:
        search_results = search_knowledge_base(user_message, n_results=2)
    except Exception as e:
        error_type = type(e).__name__
        if "InvalidSignatureException" in str(e) or "credentials" in str(e).lower():
            answer = "I'm having trouble connecting to my knowledge base (AWS credentials issue). Please check the server configuration."
        elif "ResourceNotFoundException" in str(e):
            answer = "The embedding model is not available. Please verify AWS Bedrock model access."
        elif "ThrottlingException" in str(e):
            answer = "I'm receiving too many requests right now. Please wait a moment and try again."
        else:
            answer = f"I couldn't search my knowledge base: {error_type}. Please try again later."
        current_history.append({"role": "user", "content": user_message})
        current_history.append({"role": "assistant", "content": answer})
        active_sessions[session_id] = current_history
        response_time_ms = int((time.time() - start_time) * 1000)
        conversation_id = save_conversation(session_id, user_message, answer, intent, response_time_ms)
        return {"answer": answer, "conversation_id": conversation_id}

    # Build context
    context = ""
    if search_results['documents'] and search_results['documents'][0]:
        for doc, metadata in zip(search_results['documents'][0], search_results['metadatas'][0]):
            context += f"\n[{metadata['source']}]: {doc[:800]}\n"
    else:
        context = "\nNo relevant documentation found.\n"

    # Build conversation for Claude
    system_prompt = """You are a helpful Supabase customer support agent.

Rules:
1. Answer based on the provided documentation and GitHub issues
2. Be conversational and friendly
3. If you don't know, say so honestly
4. Keep answers concise (2-3 paragraphs max)
5. Include code examples when helpful
6. Remember previous messages in the conversation"""

    # Extract recent conversation topics for better context retention
    recent_topics = []
    for msg in current_history[-8:]:
        if msg.get('role') == 'user':
            content = msg.get('content', '').lower()
            if 'oauth' in content or 'google auth' in content:
                recent_topics.append('Google OAuth setup')
            elif 'facebook' in content and 'auth' in content:
                recent_topics.append('Facebook authentication')
            elif 'github' in content and 'auth' in content:
                recent_topics.append('GitHub authentication')
            elif 'table' in content or 'create table' in content:
                recent_topics.append('database tables')
            elif 'storage' in content or 'upload' in content or 'file' in content:
                recent_topics.append('file storage')
            elif 'realtime' in content:
                recent_topics.append('realtime subscriptions')
            elif 'rls' in content or 'row level' in content:
                recent_topics.append('Row Level Security')
            elif 'edge function' in content:
                recent_topics.append('Edge Functions')

    # Build topic context summary
    topic_summary = f"Recent topics discussed: {', '.join(set(recent_topics))}\n\n" if recent_topics else ""

    # Extract recent user questions for context awareness
    recent_questions = []
    for msg in current_history[-6:]:
        if msg['role'] == 'user':
            # Get the actual question (not the prompt with documentation)
            content = msg['content']
            # Skip if it contains documentation context (from previous turns)
            if 'Relevant documentation:' not in content:
                recent_questions.append(content[:200])  # Limit length

    # Build conversation context string
    conversation_context = ""
    if recent_questions:
        conversation_context = "Recent conversation context:\n"
        for i, q in enumerate(recent_questions[-3:], 1):  # Last 3 questions
            conversation_context += f"- Previous question {i}: {q}\n"
        conversation_context += f"\nCurrent question: {user_message}\n"
    else:
        conversation_context = f"Current question: {user_message}\n"

    # Add current message with context
    user_prompt = f"""{topic_summary}{conversation_context}
Based on the conversation context and recent topics above, and the documentation below, please answer.

Relevant documentation:
{context}"""

    current_history.append({
        "role": "user",
        "content": user_prompt
    })

    # Call Claude
    try:
        # Prepare messages, ensuring first message is from user
        messages_to_send = current_history[-6:]
        if messages_to_send and messages_to_send[0]['role'] == 'assistant':
            messages_to_send = messages_to_send[1:]  # Remove leading assistant message

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 800,
            "temperature": 0.3,
            "top_p": 0.9,
            "system": system_prompt,
            "messages": messages_to_send
        })

        response = bedrock.invoke_model(
            modelId=os.getenv('BEDROCK_MODEL_ID'),
            body=body
        )

        response_body = json.loads(response['body'].read())
        answer = response_body['content'][0]['text']

    except Exception as e:
        error_type = type(e).__name__
        # Remove the failed message from history
        current_history.pop()

        if "InvalidSignatureException" in str(e) or "credentials" in str(e).lower():
            answer = "I'm having trouble connecting to Claude (AWS credentials issue). Please check the server configuration."
        elif "AccessDeniedException" in str(e):
            answer = "Access denied to Claude model. Please verify Bedrock model access permissions."
        elif "ResourceNotFoundException" in str(e):
            answer = "The Claude model is not available. Please check the BEDROCK_MODEL_ID in your .env file."
        elif "ThrottlingException" in str(e):
            answer = "I'm receiving too many requests right now. Please wait a moment and try again."
        elif "ModelTimeoutException" in str(e):
            answer = "The request timed out. Please try asking a shorter question."
        elif "ValidationException" in str(e):
            answer = f"Invalid request: {str(e)[:100]}. Please try rephrasing your question."
        else:
            answer = f"I encountered an error generating a response ({error_type}). Please try again."

        current_history.append({"role": "user", "content": user_message})
        current_history.append({"role": "assistant", "content": answer})
        active_sessions[session_id] = current_history
        response_time_ms = int((time.time() - start_time) * 1000)
        conversation_id = save_conversation(session_id, user_message, answer, intent, response_time_ms)
        return {"answer": answer, "conversation_id": conversation_id}

    # Add to history (without the context to save tokens)
    current_history[-1] = {"role": "user", "content": user_message}
    current_history.append({
        "role": "assistant",
        "content": answer
    })

    # Save session history
    active_sessions[session_id] = current_history

    # Save to database
    response_time_ms = int((time.time() - start_time) * 1000)
    conversation_id = save_conversation(session_id, user_message, answer, intent, response_time_ms)

    return {"answer": answer, "conversation_id": conversation_id}


if __name__ == "__main__":
    print("Supabase Support Agent")
    print("Type 'quit' to exit")
    print("-" * 40)

    # Generate session ID for this CLI session
    session_id = str(uuid.uuid4())
    print(f"Session ID: {session_id}")

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        if user_input:
            result = chat(user_input, session_id)
            print(f"\nAgent: {result['answer']}")
