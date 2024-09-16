# This script uses hugging face model.
# When you run this script it will make a directory called temp_repo and clone the repository in it. 
# Make sure to delete that before using this script again.

import os
import git
import shutil
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv
from langchain.llms import HuggingFaceEndpoint

load_dotenv()

api_key = os.getenv("huggingfacehub_api_token")
if not api_key:
    raise ValueError("HUGGINGFACEHUB_API_TOKEN not found in environment variables")

llm = HuggingFaceEndpoint(
    huggingfacehub_api_token=api_key,
    repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1", # Change this to the model you want to use
    temperature=0.8,
    max_new_tokens=512,
    streaming=True,
)

def CloneRepository(repo_url, local_path):
    """Clone the given repository to the specified local path."""
    if os.path.exists(local_path):
        shutil.rmtree(local_path) 
    git.Repo.clone_from(repo_url, local_path)

def ReadRepositoryContents(repo_path):
    """Read the contents of all files in the repository."""
    contents = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.startswith('.') or file == 'README.md':
                continue
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                contents.append(f.read())
    return '\n'.join(contents)

def GenerateReadme(repo_contents):
    chunk_size = 16384  # Adjust this value based on the model's limit
    chunks = [repo_contents[i:i + chunk_size] for i in range(0, len(repo_contents), chunk_size)]
    readme_contents = []
    
    for chunk in chunks:
        prompt = f"""Based on the following repository contents, generate a comprehensive README.md file
        Include these sections:
            1. Project Title
            2. Brief Description
            3. Key Features
            4. Basic Installation & Usage
            5. License (if found)

        Keep it informative. It should cover all the necssary contents in the repository.
        :\n\n{chunk}\n\nREADME.md:"""

        messages = [
            SystemMessage(content=" You are the master of README generation. No repository is too complex for you. Making readme files is a child's play for you."),
            HumanMessage(content=prompt)
        ]
        response = llm.invoke(messages)
        readme_contents.append(response)  
    
    return '\n'.join(readme_contents)

def main():
    repo_url = input("Enter the GitHub repository URL: ")
    local_path = "./temp_repo"
    
    try:
        CloneRepository(repo_url, local_path)
        
        repo_contents = ReadRepositoryContents(local_path)
        
        readme_content = GenerateReadme(repo_contents)
        
        with open("README.md", "w") as f:
            f.write(readme_content)
        
        print("README.md has been generated successfully!")
    
    finally:
        shutil.rmtree(local_path, ignore_errors=True)

if __name__ == "__main__":
    main()