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
    repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
    temperature=0.8,
    max_new_tokens=512,
    streaming=True,
)

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
                contents.append(f.read())
    return '\n'.join(contents)

def generate_readme(repo_contents):
    chunk_size = 16384  # Adjust this value based on the model's limit
    chunks = [repo_contents[i:i + chunk_size] for i in range(0, len(repo_contents), chunk_size)]
    readme_contents = []
    
    for chunk in chunks:
        prompt = f"Based on the following repository contents, generate a comprehensive README.md file:\n\n{chunk}\n\nREADME.md:"
        messages = [
            SystemMessage(content="You are a helpful assistant that generates README files for GitHub repositories."),
            HumanMessage(content=prompt)
        ]
        response = llm.invoke(messages)
        readme_contents.append(response)  # Removed .content.strip()
    
    return '\n'.join(readme_contents)

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