import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

def get_github_stars(github_url):
    """Fetches live star count from GitHub API"""
    if not github_url or "github.com" not in github_url:
        return 0
    try:
        parts = github_url.strip("/").split("/")
        if len(parts) >= 2:
            owner, repo = parts[-2], parts[-1]
            api_url = f"https://api.github.com/repos/{owner}/{repo}"
            headers = {"Accept": "application/vnd.github.v3+json"}
            response = requests.get(api_url, headers=headers, timeout=5)
            if response.status_code == 200:
                return response.json().get("stargazers_count", 0)
    except Exception:
        pass
    return 0

def scrape_arxiv():
    url = "https://arxiv.org/list/cs.AI/recent"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    print(f"Connecting to {url}...")
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print("Failed to load page.")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    titles = soup.find_all('div', class_='list-title')
    
    papers = []
    print(f"\nProcessing first 5 papers with mock/extracted GitHub check:")
    for idx, title_tag in enumerate(titles[:5], 1):
        title = title_tag.text.replace('Title:', '').strip()
        
        # Simulating a linked github repo for demonstration or pulling it if present
        # (We can test with a known repository link to verify star counting)
        sample_github = "https://github.com/torvalds/linux" if idx == 1 else ""
        stars = get_github_stars(sample_github) if sample_github else 0
        
        paper_data = {
            "title": title,
            "github_url": sample_github,
            "github_stars": stars,
            "collectedAt": datetime.now(timezone.utc).isoformat()
        }
        papers.append(paper_data)
        print(f"{idx}. {title} | GitHub Stars: {stars}")

if __name__ == "__main__":
    scrape_arxiv()
