import requests
import json
import os
import time
from dotenv import load_dotenv

# Get project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(os.path.join(PROJECT_ROOT, '.env'))


def scrape_github_issues():
    """
    Scrape closed GitHub issues from Supabase repo
    Focus on issues with solutions (closed issues)
    """
    print("Starting GitHub issues scraper...")

    # Create folder for GitHub data
    github_path = os.path.join(PROJECT_ROOT, 'data', 'raw', 'github')
    if not os.path.exists(github_path):
        os.makedirs(github_path)

    # GitHub API setup
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Supabase repository
    repo = "supabase/supabase"

    # Get closed issues (these usually have solutions)
    # We'll get issues labeled as 'bug' or 'question' that are closed
    labels = ['bug', 'question']

    all_issues = []

    for label in labels:
        print(f"\nFetching '{label}' issues...")

        url = f"https://api.github.com/repos/{repo}/issues"
        params = {
            'state': 'closed',
            'labels': label,
            'per_page': 20,  # Get 20 issues per label
            'sort': 'comments',  # Get issues with most discussion
            'direction': 'desc'
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            issues = response.json()

            print(f"Found {len(issues)} closed '{label}' issues")

            for issue in issues:
                # Skip pull requests
                if 'pull_request' in issue:
                    continue

                issue_data = {
                    'number': issue['number'],
                    'title': issue['title'],
                    'body': issue.get('body', ''),
                    'labels': [l['name'] for l in issue.get('labels', [])],
                    'state': issue['state'],
                    'comments_count': issue['comments'],
                    'url': issue['html_url'],
                    'created_at': issue['created_at'],
                    'closed_at': issue.get('closed_at', '')
                }

                # Get comments (solutions are often in comments)
                if issue['comments'] > 0:
                    comments_url = issue['comments_url']
                    comments_response = requests.get(comments_url, headers=headers)

                    if comments_response.status_code == 200:
                        comments = comments_response.json()
                        issue_data['comments'] = [
                            {
                                'author': c['user']['login'],
                                'body': c['body'],
                                'created_at': c['created_at']
                            }
                            for c in comments[:5]  # Get first 5 comments
                        ]

                    # Be nice to GitHub API
                    time.sleep(1)

                all_issues.append(issue_data)

                # Save individual issue as text file
                filename = f"issue_{issue['number']}_{label}.txt"
                filepath = os.path.join(github_path, filename)

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"Issue #{issue['number']}: {issue['title']}\n")
                    f.write(f"URL: {issue['html_url']}\n")
                    f.write(f"Labels: {', '.join(issue_data['labels'])}\n")
                    f.write(f"Status: {issue['state']}\n")
                    f.write(f"{'='*80}\n\n")
                    f.write("PROBLEM:\n")
                    f.write(issue_data['body'] or "No description provided")
                    f.write("\n\n")

                    if 'comments' in issue_data and issue_data['comments']:
                        f.write("DISCUSSION/SOLUTIONS:\n")
                        for i, comment in enumerate(issue_data['comments'], 1):
                            f.write(f"\n--- Comment {i} by {comment['author']} ---\n")
                            f.write(comment['body'])
                            f.write("\n")

                print(f"  Saved issue #{issue['number']}: {issue['title'][:50]}...")

            # Wait between label requests
            time.sleep(2)

        except Exception as e:
            print(f"Error fetching '{label}' issues: {e}")

    print("\n" + "="*80)
    print("GitHub scraping complete! Collected " + str(len(all_issues)) + " issues")
    print(f"Files saved in: {github_path}")

    return len(all_issues)


if __name__ == "__main__":
    scrape_github_issues()
