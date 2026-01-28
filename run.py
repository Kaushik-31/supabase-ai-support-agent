"""
Convenience script to run the Supabase Support Agent web app
"""
import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from backend.api.app import app

if __name__ == '__main__':
    print("Starting Supabase Support Agent...")
    print("Open http://localhost:5000 in your browser")
    print("-" * 40)
    app.run(debug=True, port=5000)
