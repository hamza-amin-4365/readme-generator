import os
import json
import git
from pathlib import Path

def clone_repo(repo_url, clone_dir):
    """Clone a GitHub repo to a local directory."""
    git.Repo.clone_from(repo_url, clone_dir)

def extract_repo_info(repo_path):
    """Extract key files and README content from the repo."""
    repo_data = {}
    repo_name = os.path.basename(repo_path)
    repo_data["repo_name"] = repo_name
    repo_data["files"] = []
    
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file == "README.md":
                with open(file_path, 'r') as f:
                    repo_data["readme"] = f.read()
            else:
                repo_data["files"].append({
                    "file_name": file,
                    "description": get_file_description(file_path)
                })
    
    return repo_data

def get_file_description(file_path):
    """Simple heuristic to extract basic info from a file."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        # Extract comments or first lines as description
        lines = file.readlines()
        description = ' '.join([line.strip() for line in lines[:10]])
    return description

def save_to_json(data, output_path):
    """Save the extracted repo info to a JSON file."""
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)

# Example usage:
repo_url = 'https://github.com/some/repo.git'  # Replace with actual repo
clone_dir = '/content/repo'  # Or other directory
output_json = '/content/repo_data.json'

# Step-by-step
clone_repo(repo_url, clone_dir)
repo_data = extract_repo_info(clone_dir)
save_to_json(repo_data, output_json)
