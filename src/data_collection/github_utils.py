import os
import base64
import time
from typing import List, Dict, Any
import requests
import json
from dataclasses import dataclass, asdict
from tqdm import tqdm
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# GitHub API configuration
GITHUB_API_URL = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise ValueError("GitHub token not found. Please set the GITHUB_TOKEN environment variable.")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

@dataclass
class RepoData:
    repo_name: str
    file_structure: Dict[str, Any]
    readme_content: str

def get_repo_contents(owner: str, repo: str, path: str = "") -> Dict[str, Any]:
    """Recursively fetch repository contents."""
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/contents/{path}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    contents = response.json()

    if isinstance(contents, list):
        return {
            item['name']: get_repo_contents(owner, repo, f"{path}/{item['name']}") if item['type'] == 'dir'
            else item['type']
            for item in contents
        }
    else:
        return contents['type']

def get_readme_content(owner: str, repo: str) -> str:
    """Fetch README content from a repository."""
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/readme"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    content = response.json()['content']
    return base64.b64decode(content).decode('utf-8')

def search_repos(query: str, max_results: int = 100) -> List[Dict[str, Any]]:
    """Search for repositories on GitHub."""
    url = f"{GITHUB_API_URL}/search/repositories"
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": 100
    }
    
    all_repos = []
    page = 1
    
    with tqdm(total=max_results, desc="Fetching repositories") as pbar:
        while len(all_repos) < max_results:
            params["page"] = page
            response = requests.get(url, headers=HEADERS, params=params)
            response.raise_for_status()
            repos = response.json()['items']
            
            if not repos:
                break
            
            all_repos.extend(repos[:max_results - len(all_repos)])
            pbar.update(len(repos))
            page += 1
            time.sleep(1)  # Respect GitHub API rate limits
    
    return all_repos[:max_results]

def collect_data(query: str, max_repos: int = 100) -> List[RepoData]:
    """Collect data from GitHub repositories."""
    repos = search_repos(query, max_repos)
    data = []

    for repo in tqdm(repos, desc="Processing repositories"):
        owner, name = repo['full_name'].split('/')
        try:
            file_structure = get_repo_contents(owner, name)
            readme_content = get_readme_content(owner, name)
            data.append(RepoData(repo['full_name'], file_structure, readme_content))
        except requests.exceptions.RequestException as e:
            logger.error(f"Error processing repository {repo['full_name']}: {str(e)}")
        time.sleep(1)  # Respect GitHub API rate limits

    return data

def save_data(data: List[RepoData], output_dir: str):
    """Save collected data to files."""
    os.makedirs(output_dir, exist_ok=True)
    
    for item in data:
        repo_dir = os.path.join(output_dir, item.repo_name.replace('/', '_'))
        os.makedirs(repo_dir, exist_ok=True)
        
        # Save file structure
        with open(os.path.join(repo_dir, 'file_structure.json'), 'w') as f:
            json.dump(item.file_structure, f, indent=2)
        
        # Save README content
        with open(os.path.join(repo_dir, 'readme.md'), 'w') as f:
            f.write(item.readme_content)

if __name__ == "__main__":
    query = "stars:>100 language:python"  # Example query
    max_repos = 5  # Adjust as needed
    output_dir = "github_data"

    logger.info(f"Starting data collection for query: {query}")
    data = collect_data(query, max_repos)
    logger.info(f"Collected data from {len(data)} repositories")

    logger.info(f"Saving data to {output_dir}")
    save_data(data, output_dir)
    logger.info("Data collection complete")