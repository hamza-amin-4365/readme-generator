import os
import json
import pandas as pd
from tqdm import tqdm

MIRROR_DIRECTORY = "hf_public_repos"
OUTPUT_FILE = "readme_data_sample.feather"
MAX_REPOS = 5  # Adjust this to process more or fewer repositories

def get_file_structure(repo_path):
    """Returns a JSON representation of the repository structure."""
    structure = {}
    for root, dirs, files in os.walk(repo_path):
        current = structure
        path = os.path.relpath(root, repo_path).split(os.sep)
        for part in path:
            if part not in current:
                current[part] = {}
            current = current[part]
        current['_files'] = files
    return json.dumps(structure)

def process_repository(repo_path):
    """Processes a single repository."""
    repo_id = os.path.basename(repo_path)
    readme_path = os.path.join(repo_path, 'README.md')
    
    file_structure = get_file_structure(repo_path)
    
    readme_content = ""
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as file:
            readme_content = file.read()
    
    return {
        "repo_id": repo_id,
        "file_structure": file_structure,
        "readme_content": readme_content,
    }

def read_repositories(directory, max_repos):
    """Reads the README files and structures from the locally cloned repositories."""
    df = pd.DataFrame(columns=["repo_id", "file_structure", "readme_content"])

    repo_paths = [os.path.join(directory, name) for name in os.listdir(directory)
                  if os.path.isdir(os.path.join(directory, name))][:max_repos]

    print(f"Processing {len(repo_paths)} repositories...")

    for repo_path in tqdm(repo_paths):
        repo_data = process_repository(repo_path)
        temp_df = pd.DataFrame.from_dict([repo_data])
        df = pd.concat([df, temp_df])

    return df

if __name__ == "__main__":
    df = read_repositories(MIRROR_DIRECTORY, MAX_REPOS)
    print(f"DataFrame created with {len(df)} rows.")
    
    # Save the DataFrame locally
    df.reset_index(drop=True).to_feather(OUTPUT_FILE)
    print(f"Data saved to {OUTPUT_FILE}")

    # Print a sample of the data
    print("\nSample of the data:")
    print(df.head())
    
    # Print some statistics
    print("\nDataset statistics:")
    print(f"Number of repositories: {len(df)}")
    print(f"Average README length: {df['readme_content'].str.len().mean():.2f} characters")
    print(f"Repositories with README: {df['readme_content'].str.len().gt(0).sum()}")