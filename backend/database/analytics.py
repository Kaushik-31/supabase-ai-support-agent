from .database import get_connection


def get_conversation_stats(days=7):
    """Get conversation statistics for the past N days"""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT
        COUNT(*) as total_conversations,
        COUNT(DISTINCT session_id) as unique_sessions,
        AVG(response_time_ms) as avg_response_time,
        MIN(created_at) as first_conversation,
        MAX(created_at) as last_conversation
    FROM conversations
    WHERE created_at >= NOW() - INTERVAL '%s days';
    """

    try:
        cursor.execute(query, (days,))
        result = cursor.fetchone()
        return {
            'total_conversations': result[0],
            'unique_sessions': result[1],
            'avg_response_time_ms': round(result[2], 2) if result[2] else 0,
            'first_conversation': result[3],
            'last_conversation': result[4]
        }
    finally:
        cursor.close()
        conn.close()


def get_intent_distribution(days=7):
    """Get distribution of intents for the past N days"""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT
        intent,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
    FROM conversations
    WHERE created_at >= NOW() - INTERVAL '%s days'
    GROUP BY intent
    ORDER BY count DESC;
    """

    try:
        cursor.execute(query, (days,))
        results = cursor.fetchall()
        return [
            {'intent': row[0], 'count': row[1], 'percentage': float(row[2])}
            for row in results
        ]
    finally:
        cursor.close()
        conn.close()


def get_daily_conversations(days=7):
    """Get conversation count per day for the past N days"""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT
        DATE(created_at) as date,
        COUNT(*) as count
    FROM conversations
    WHERE created_at >= NOW() - INTERVAL '%s days'
    GROUP BY DATE(created_at)
    ORDER BY date;
    """

    try:
        cursor.execute(query, (days,))
        results = cursor.fetchall()
        return [
            {'date': row[0].isoformat(), 'count': row[1]}
            for row in results
        ]
    finally:
        cursor.close()
        conn.close()


def get_slow_responses(threshold_ms=5000, limit=10):
    """Get conversations with slow response times"""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT
        id,
        session_id,
        user_message,
        intent,
        response_time_ms,
        created_at
    FROM conversations
    WHERE response_time_ms > %s
    ORDER BY response_time_ms DESC
    LIMIT %s;
    """

    try:
        cursor.execute(query, (threshold_ms, limit))
        results = cursor.fetchall()
        return [
            {
                'id': row[0],
                'session_id': str(row[1]),
                'user_message': row[2][:100] + '...' if len(row[2]) > 100 else row[2],
                'intent': row[3],
                'response_time_ms': row[4],
                'created_at': row[5].isoformat()
            }
            for row in results
        ]
    finally:
        cursor.close()
        conn.close()


def get_total_queries():
    """Get total count of all conversations"""
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT COUNT(*) FROM conversations;"

    try:
        cursor.execute(query)
        result = cursor.fetchone()
        return result[0] if result else 0
    finally:
        cursor.close()
        conn.close()


def get_queries_today():
    """Get count of conversations from today"""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT COUNT(*) FROM conversations
    WHERE DATE(created_at) = CURRENT_DATE;
    """

    try:
        cursor.execute(query)
        result = cursor.fetchone()
        return result[0] if result else 0
    finally:
        cursor.close()
        conn.close()


def get_queries_by_date(days=7):
    """Get queries per day for last N days, formatted for charts"""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT
        DATE(created_at) as date,
        COUNT(*) as count
    FROM conversations
    WHERE created_at >= NOW() - INTERVAL '%s days'
    GROUP BY DATE(created_at)
    ORDER BY date;
    """

    try:
        cursor.execute(query, (days,))
        results = cursor.fetchall()
        return {
            'labels': [row[0].strftime('%Y-%m-%d') for row in results],
            'data': [row[1] for row in results]
        }
    finally:
        cursor.close()
        conn.close()


def get_top_intents(limit=5):
    """Get most common intent types, formatted for charts"""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT
        COALESCE(intent, 'unknown') as intent,
        COUNT(*) as count
    FROM conversations
    GROUP BY intent
    ORDER BY count DESC
    LIMIT %s;
    """

    try:
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        return {
            'labels': [row[0] for row in results],
            'data': [row[1] for row in results]
        }
    finally:
        cursor.close()
        conn.close()


def get_average_response_time():
    """Get average response time in milliseconds"""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT
        AVG(response_time_ms) as avg_time,
        MIN(response_time_ms) as min_time,
        MAX(response_time_ms) as max_time
    FROM conversations
    WHERE response_time_ms IS NOT NULL;
    """

    try:
        cursor.execute(query)
        result = cursor.fetchone()
        return {
            'average_ms': round(result[0], 2) if result[0] else 0,
            'min_ms': result[1] if result[1] else 0,
            'max_ms': result[2] if result[2] else 0
        }
    finally:
        cursor.close()
        conn.close()


def get_feedback_stats():
    """Get thumbs up/down counts and percentages"""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT
        COUNT(*) FILTER (WHERE rating = 1) as thumbs_up,
        COUNT(*) FILTER (WHERE rating = -1) as thumbs_down,
        COUNT(*) FILTER (WHERE rating IS NOT NULL) as total_rated,
        COUNT(*) as total_conversations
    FROM conversations;
    """

    try:
        cursor.execute(query)
        result = cursor.fetchone()
        thumbs_up = result[0] or 0
        thumbs_down = result[1] or 0
        total_rated = result[2] or 0
        total_conversations = result[3] or 0

        return {
            'thumbs_up': thumbs_up,
            'thumbs_down': thumbs_down,
            'total_rated': total_rated,
            'total_conversations': total_conversations,
            'thumbs_up_percent': round((thumbs_up / total_rated * 100), 1) if total_rated > 0 else 0,
            'thumbs_down_percent': round((thumbs_down / total_rated * 100), 1) if total_rated > 0 else 0,
            'feedback_rate': round((total_rated / total_conversations * 100), 1) if total_conversations > 0 else 0
        }
    finally:
        cursor.close()
        conn.close()


def get_most_asked_questions(limit=10):
    """Get most frequent user messages"""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT
        user_message,
        COUNT(*) as count,
        intent
    FROM conversations
    WHERE intent = 'question'
    GROUP BY user_message, intent
    ORDER BY count DESC
    LIMIT %s;
    """

    try:
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        return [
            {
                'question': row[0][:100] + '...' if len(row[0]) > 100 else row[0],
                'count': row[1],
                'intent': row[2]
            }
            for row in results
        ]
    finally:
        cursor.close()
        conn.close()


def get_recent_conversations(limit=20):
    """Get most recent conversations"""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT
        id,
        session_id,
        user_message,
        bot_response,
        intent,
        response_time_ms,
        rating,
        created_at
    FROM conversations
    ORDER BY created_at DESC
    LIMIT %s;
    """

    try:
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        return [
            {
                'id': row[0],
                'session_id': str(row[1])[:8] + '...',
                'user_message': row[2][:50] + '...' if len(row[2]) > 50 else row[2],
                'bot_response': row[3][:50] + '...' if len(row[3]) > 50 else row[3],
                'intent': row[4] or 'unknown',
                'response_time_ms': row[5] or 0,
                'rating': row[6],
                'created_at': row[7].strftime('%Y-%m-%d %H:%M') if row[7] else ''
            }
            for row in results
        ]
    finally:
        cursor.close()
        conn.close()
