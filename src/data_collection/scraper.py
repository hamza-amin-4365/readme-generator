import os
import json
import git
import shutil
import stat
from pathlib import Path

def on_rm_error(func, path, exc_info):
    """Error handler for `shutil.rmtree` to handle read-only files."""
    # Change file permissions and retry
    os.chmod(path, stat.S_IWRITE)
    func(path)

def clone_repo(repo_url, clone_dir):
    """Clone a GitHub repo to a local directory."""
    if os.path.exists(clone_dir):
        print(f"Directory {clone_dir} already exists. Removing it.")
        shutil.rmtree(clone_dir, onerror=on_rm_error)  # Use custom error handler
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
repo_url = 'https://github.com/hamza-amin-4365/Chat-with-sql.git'  # Replace with actual repo
# Change this to a valid path on your local machine
clone_dir = '/repo_data'

output_json = 'repo_data.json'

# Step-by-step
clone_repo(repo_url, clone_dir)
repo_data = extract_repo_info(clone_dir)
save_to_json(repo_data, output_json)
