import os
import git
import shutil
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv


load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
llm = ChatOpenAI(model_name='gpt-4o-mini')


def clone_repository(repo_url, local_path):
    """Clone the given repository to the specified local path."""
    if os.path.exists(local_path):
        shutil.rmtree(local_path)  # Remove the directory if it already exists
    git.Repo.clone_from(repo_url, local_path)

def read_repository_contents(repo_path):
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

def generate_readme(repo_contents):
    """Generate a README file using GPT-4."""
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
        # Clone the repository
        clone_repository(repo_url, local_path)
        
        # Read the repository contents
        repo_contents = read_repository_contents(local_path)
        
        # Generate the README
        readme_content = generate_readme(repo_contents)
        
        # Save the README
        with open("README.md", "w") as f:
            f.write(readme_content)
        
        print("README.md has been generated successfully!")
    
    finally:
        # Clean up: remove the cloned repository
        shutil.rmtree(local_path, ignore_errors=True)

if __name__ == "__main__":
    main()