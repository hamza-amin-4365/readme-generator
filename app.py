# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# This script has the highest accuracy in making readme files. When you run this script it will make a directory 
# called temp_repo and clone the repository in it. Make sure to delete that before using this script again.

import os
import git
import shutil
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv


load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
llm = ChatOpenAI(model_name='gpt-4o-mini')


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
                contents.append(f"File: {file_path}\n\n{f.read()}\n\n")
    return '\n'.join(contents)

def GenerateReadme(repo_contents):
    """Generate a README file using GPT-4o-mini."""
    prompt = f"Based on the following repository contents, generate a comprehensive README.md file:\n\n{repo_contents}\n\nREADME.md:"
    
    messages = [
        SystemMessage(content="You are a helpful assistant that generates README files for GitHub repositories."),
        HumanMessage(content=prompt)
    ]
    
    response = llm.invoke(messages)
    
    return response.content.strip()

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