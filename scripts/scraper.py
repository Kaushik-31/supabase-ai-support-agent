import requests
from bs4 import BeautifulSoup
import time
import os

# Get project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def scrape_supabase_docs():
    """
    Scrape Supabase documentation pages
    """
    print("Starting Supabase documentation scraper...")

    # Create folder for scraped data
    data_path = os.path.join(PROJECT_ROOT, 'data')
    raw_path = os.path.join(data_path, 'raw')

    if not os.path.exists(data_path):
        os.makedirs(data_path)
    if not os.path.exists(raw_path):
        os.makedirs(raw_path)

    # List of important Supabase doc pages to scrape
    doc_urls = [
        "https://supabase.com/docs/guides/getting-started",
        "https://supabase.com/docs/guides/auth",
        "https://supabase.com/docs/guides/database",
        "https://supabase.com/docs/guides/api",
        "https://supabase.com/docs/guides/storage",
        "https://supabase.com/docs/guides/realtime",
        "https://supabase.com/docs/guides/auth/social-login/auth-google",
        "https://supabase.com/docs/guides/database/tables",
        "https://supabase.com/docs/guides/auth/passwords",
        "https://supabase.com/docs/reference/javascript/introduction",
    ]

    scraped_count = 0

    for url in doc_urls:
        try:
            print(f"\nScraping: {url}")

            # Get the page
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title = soup.find('h1')
            title_text = title.get_text().strip() if title else "Untitled"

            # Extract main content
            # Supabase docs usually in article or main tags
            content = soup.find('article') or soup.find('main')

            if content:
                # Get text content
                text = content.get_text(separator='\n', strip=True)

                # Create filename from URL
                filename = url.replace('https://supabase.com/docs/', '').replace('/', '_')
                filename = f"{filename}.txt"

                # Save to file
                filepath = os.path.join(raw_path, filename)

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"Title: {title_text}\n")
                    f.write(f"URL: {url}\n")
                    f.write(f"{'='*80}\n\n")
                    f.write(text)

                print(f"Saved: {filename} ({len(text)} characters)")
                scraped_count += 1
            else:
                print(f"No content found on {url}")

            # Be nice to the server - wait between requests
            time.sleep(2)

        except Exception as e:
            print(f"Error scraping {url}: {e}")

    print(f"\n{'='*80}")
    print(f"Scraping complete! Collected {scraped_count} documents")
    print(f"Files saved in: {raw_path}")

    return scraped_count


if __name__ == "__main__":
    scrape_supabase_docs()
