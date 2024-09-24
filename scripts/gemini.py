# This can handle large repos too. 
# Description: This script generates a README file for a GitHub repository using the Gemini API.
# python gemini.py <repository_url>

import os
import git
import shutil
import tempfile
from pathlib import Path
from google.generativeai import GenerativeModel, configure
from dotenv import load_dotenv
import logging
import argparse
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

configure(api_key=os.getenv('GEMINI_API_KEY'))
model = GenerativeModel('gemini-pro')

MAX_CONTENT_LENGTH = 100000  # Adjust this based on Gemini's actual limit
RATE_LIMIT_DELAY = 60  # Delay in seconds when rate limit is hit

def CloneRepository(repo_url, local_path):
    """Clone the given repository to the specified local path."""
    try:
        if os.path.exists(local_path):
            shutil.rmtree(local_path)
        git.Repo.clone_from(repo_url, local_path)
        logger.info(f"Repository cloned successfully to {local_path}")
    except git.GitCommandError as e:
        logger.error(f"Failed to clone repository: {e}")
        raise

def GetImportantFiles(repo_path):
    """Get a list of important files for README generation."""
    important_files = []
    important_patterns = [
        '*.py', '*.js', '*.ts', '*.java', '*.cpp', '*.h',
        'Dockerfile', 'docker-compose.yml',
        'requirements.txt', 'package.json', 'pom.xml', 'build.gradle',
        '.gitignore', '.env.example',
        'LICENSE', 'CONTRIBUTING.md'
    ]
    
    for pattern in important_patterns:
        important_files.extend(Path(repo_path).glob('**/' + pattern))
    
    return important_files[:10]  # Limit to top 10 files

def ReadFilePreview(file_path, max_lines=50):
    """Read a preview of the file contents."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            preview = ''.join(lines[:max_lines])
            return f"File: {file_path}\n\n{preview}\n\n"
    except Exception as e:
        logger.warning(f"Failed to read file {file_path}: {e}")
        return ""

def ReadRepositoryContents(repo_path):
    """Read the contents of important files in the repository."""
    important_files = GetImportantFiles(repo_path)
    contents = [ReadFilePreview(file) for file in important_files]
    return '\n'.join(contents)

def GenerateReadme(repo_contents):
    """Generate a README file using Gemini API with rate limit handling."""
    prompt = f"""
    Based on the following repository preview, generate a comprehensive README.md file:

    {repo_contents}

    Include these sections:
    1. Project Title
    2. Brief Description
    3. Key Features
    4. Basic Installation & Usage
    5. License (if found)

    Keep it informative. It should cover all the necssary contents in the repository.
    """
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            if 'Resource has been exhausted' in str(e) and attempt < max_retries - 1:
                logger.warning(f"Rate limit hit. Waiting for {RATE_LIMIT_DELAY} seconds before retrying...")
                time.sleep(RATE_LIMIT_DELAY)
            else:
                logger.error(f"Failed to generate README: {e}")
                raise

def main(repo_url, output_path):
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            CloneRepository(repo_url, temp_dir)
            
            logger.info("Reading repository contents...")
            repo_contents = ReadRepositoryContents(temp_dir)
            
            logger.info("Generating README...")
            readme_content = GenerateReadme(repo_contents)
            
            output_file = Path(output_path) / "README.md"
            with open(output_file, "w") as f:
                f.write(readme_content)
            
            logger.info(f"README.md has been generated successfully at {output_file}")
        
        except Exception as e:
            logger.error(f"An error occurred: {e}")
        
        finally:
            logger.info("Cleaning up temporary files...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate README for a GitHub repository")
    parser.add_argument("repo_url", help="URL of the GitHub repository")
    parser.add_argument("--output", default=".", help="Output directory for README.md")
    args = parser.parse_args()

    main(args.repo_url, args.output)