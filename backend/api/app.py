import os
import sys
import uuid
from dotenv import load_dotenv

# Get project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

# Add project root to path for imports
sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from backend.agents.chat import chat
from backend.database.database import save_feedback
from backend.database.analytics import (
    get_total_queries,
    get_queries_today,
    get_queries_by_date,
    get_top_intents,
    get_average_response_time,
    get_feedback_stats,
    get_most_asked_questions,
    get_recent_conversations
)

# Set template and static folders relative to project root
app = Flask(
    __name__,
    template_folder=os.path.join(PROJECT_ROOT, 'frontend', 'templates'),
    static_folder=os.path.join(PROJECT_ROOT, 'frontend', 'static')
)
CORS(app, supports_credentials=True)

# Secret key for Flask sessions
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24).hex())


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.get_json()

    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400

    user_message = data['message']

    # Get or create session_id for this user
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    session_id = session['session_id']

    try:
        # chat() returns dict with 'answer' and 'conversation_id'
        result = chat(user_message, session_id)
        return jsonify({
            'response': result['answer'],
            'conversation_id': result['conversation_id'],
            'session_id': session_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/feedback', methods=['POST'])
def feedback_endpoint():
    data = request.get_json()

    if not data or 'conversation_id' not in data or 'rating' not in data:
        return jsonify({'error': 'conversation_id and rating are required'}), 400

    conversation_id = data['conversation_id']
    rating = data['rating']
    feedback_text = data.get('feedback_text')

    # Validate rating
    if rating not in (1, -1):
        return jsonify({'error': 'Rating must be 1 (thumbs up) or -1 (thumbs down)'}), 400

    try:
        result = save_feedback(conversation_id, rating, feedback_text)
        if result:
            return jsonify({'success': True, 'conversation_id': result})
        else:
            return jsonify({'error': 'Conversation not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/stats')
def stats_endpoint():
    """Get quick stats for the chat header"""
    try:
        response_time = get_average_response_time()
        return jsonify({
            'online': True,
            'queries_today': get_queries_today(),
            'avg_response_time_ms': response_time['average_ms']
        })
    except Exception as e:
        return jsonify({
            'online': False,
            'queries_today': 0,
            'avg_response_time_ms': 0,
            'error': str(e)
        })


@app.route('/dashboard')
def dashboard():
    """Analytics dashboard page"""
    try:
        data = {
            'total_queries': get_total_queries(),
            'queries_by_date': get_queries_by_date(days=7),
            'top_intents': get_top_intents(limit=5),
            'response_time': get_average_response_time(),
            'feedback_stats': get_feedback_stats(),
            'top_questions': get_most_asked_questions(limit=10),
            'recent_conversations': get_recent_conversations(limit=20)
        }
        return render_template('dashboard.html', **data)
    except Exception as e:
        return render_template('dashboard.html', error=str(e))


if __name__ == '__main__':
    app.run(debug=True, port=5000)
