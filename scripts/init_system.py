"""
Initialize the entire system:
1. Scrape Supabase documentation
2. Scrape GitHub issues
3. Load data into ChromaDB
4. Initialize the database
"""
import os
import sys

# Get project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from scripts.scraper import scrape_supabase_docs
from scripts.github_scraper import scrape_github_issues
from scripts.load_data_to_chromadb import load_documents
from backend.database.database import init_database


def init_system(skip_scraping=False):
    """Initialize the complete system"""

    print("="*80)
    print("INITIALIZING SUPABASE SUPPORT AGENT SYSTEM")
    print("="*80)

    # Step 1: Scrape documentation
    if not skip_scraping:
        print("\n[Step 1/4] Scraping Supabase documentation...")
        print("-"*40)
        doc_count = scrape_supabase_docs()
        print(f"Scraped {doc_count} documentation pages")

        # Step 2: Scrape GitHub issues
        print("\n[Step 2/4] Scraping GitHub issues...")
        print("-"*40)
        issue_count = scrape_github_issues()
        print(f"Scraped {issue_count} GitHub issues")
    else:
        print("\n[Step 1/4] Skipping documentation scraping...")
        print("[Step 2/4] Skipping GitHub issues scraping...")

    # Step 3: Load data into ChromaDB
    print("\n[Step 3/4] Loading data into ChromaDB...")
    print("-"*40)
    loaded_count = load_documents()
    print(f"Loaded {loaded_count} documents into ChromaDB")

    # Step 4: Initialize PostgreSQL database
    print("\n[Step 4/4] Initializing PostgreSQL database...")
    print("-"*40)
    try:
        init_database()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Warning: Could not initialize database: {e}")
        print("Make sure PostgreSQL is running and .env has correct credentials")

    print("\n" + "="*80)
    print("SYSTEM INITIALIZATION COMPLETE!")
    print("="*80)
    print("\nYou can now run the web app with:")
    print("  python backend/api/app.py")
    print("\nOr test the agent directly with:")
    print("  python backend/agents/chat.py")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Initialize the Supabase Support Agent system')
    parser.add_argument('--skip-scraping', action='store_true',
                        help='Skip scraping and only load existing data')

    args = parser.parse_args()
    init_system(skip_scraping=args.skip_scraping)
