import os
import json
import pandas as pd
import logging
from nbformat import reads, NO_CONVERT
from tqdm import tqdm
from datasets import Dataset
from typing import Dict, List, Optional, Tuple
from huggingface_hub import create_repo, upload_folder
import tempfile
import shutil

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
MIRROR_DIRECTORY = "hf_public_repos"
DATASET_ID = "hamza-amin/readme-gen-data"
SERIALIZE_IN_CHUNKS = 10000
FEATHER_FORMAT = "ftr"

# Anti-formats (keeping the original lists)
IMAGE = ["png", "jpg", "jpeg", "gif"]
VIDEO = ["mp4", "jfif"]
DOC = ["key", "PDF", "pdf", "docx", "xlsx", "pptx"]
AUDIO = ["flac", "ogg", "mid", "webm", "wav", "mp3"]
ARCHIVE = ["jar", "aar", "gz", "zip", "bz2"]
MODEL = ["onnx", "pickle", "model", "neuron"]
OTHERS = [
    "npy", "index", "inv", "DS_Store", "rdb", "pack", "idx", "glb",
    "gltf", "len", "otf", "unitypackage", "ttf", "xz", "pcm", "opus"
]
ANTI_FORMATS = tuple(IMAGE + VIDEO + DOC + AUDIO + ARCHIVE + MODEL + OTHERS)

# Key file patterns to identify important code files
KEY_FILE_PATTERNS = [
    "main", "index", "app", "setup.py", "package.json", 
    "requirements.txt", "Dockerfile", "docker-compose.yml"
]

class RepoProcessor:
    def __init__(self, directory: str):
        self.directory = directory
        self.df = pd.DataFrame(columns=["repo_id", "file_structure", "readme_content", "key_code_snippets"])
        self.chunk_flag = 0

    def _is_key_file(self, file_path: str) -> bool:
        """Determine if a file is a key file based on patterns."""
        file_name = os.path.basename(file_path).lower()
        return any(pattern.lower() in file_name for pattern in KEY_FILE_PATTERNS)

    def _read_file_content(self, file_path: str) -> Optional[str]:
        """Safely read file content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if file_path.endswith('.ipynb'):
                    return self._process_notebook(content)
                return content
        except Exception as e:
            logger.warning(f"Error reading file {file_path}: {e}")
            return None

    def _process_notebook(self, content: str) -> str:
        """Process Jupyter notebook content."""
        try:
            notebook = reads(content, NO_CONVERT)
            code_cells = [
                c["source"] for c in notebook["cells"]
                if c["cell_type"] == "code" and not (
                    c["source"].startswith("!") or 
                    "%%capture" in c["source"]
                )
            ]
            return "\n".join(code_cells)
        except Exception as e:
            logger.warning(f"Error processing notebook: {e}")
            return ""

    def _build_file_structure(self, start_path: str) -> Dict:
        """Build a JSON representation of the file structure."""
        structure = {
            "type": "directory",
            "name": os.path.basename(start_path),
            "children": []
        }
        
        try:
            for item in os.listdir(start_path):
                full_path = os.path.join(start_path, item)
                if any(k in full_path for k in [".git", "__pycache__", "xcodeproj"]):
                    continue
                    
                if os.path.isfile(full_path) and not item.endswith(ANTI_FORMATS):
                    structure["children"].append({
                        "type": "file",
                        "name": item
                    })
                elif os.path.isdir(full_path):
                    structure["children"].append(
                        self._build_file_structure(full_path)
                    )
        except Exception as e:
            logger.error(f"Error building file structure for {start_path}: {e}")
        
        return structure

    def process_repository(self, repo_path: str) -> Tuple[Dict, Dict, Optional[str]]:
        """Process a single repository."""
        file_structure = self._build_file_structure(repo_path)
        key_code_snippets = {}
        readme_content = None

        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.lower().startswith('readme.') and not file.endswith(ANTI_FORMATS):
                    readme_path = os.path.join(root, file)
                    readme_content = self._read_file_content(readme_path)
                    continue

                file_path = os.path.join(root, file)
                if not file_path.endswith(ANTI_FORMATS) and self._is_key_file(file_path):
                    content = self._read_file_content(file_path)
                    if content:
                        relative_path = os.path.relpath(file_path, repo_path)
                        key_code_snippets[relative_path] = content

        return file_structure, key_code_snippets, readme_content

    def process_repositories(self):
        """Process all repositories in the directory."""
        repo_dirs = [d for d in os.listdir(self.directory) 
                    if os.path.isdir(os.path.join(self.directory, d))]
        
        for repo_dir in tqdm(repo_dirs, desc="Processing repositories"):
            full_path = os.path.join(self.directory, repo_dir)
            try:
                file_structure, key_code_snippets, readme_content = self.process_repository(full_path)
                
                repo_data = {
                    "repo_id": repo_dir,
                    "file_structure": json.dumps(file_structure),
                    "readme_content": readme_content or "",
                    "key_code_snippets": json.dumps(key_code_snippets)
                }
                
                self.df = pd.concat([self.df, pd.DataFrame([repo_data])], ignore_index=True)
                
                if SERIALIZE_IN_CHUNKS and len(self.df) >= SERIALIZE_IN_CHUNKS:
                    self._serialize_chunk()
                    
            except Exception as e:
                logger.error(f"Error processing repository {repo_dir}: {e}")

        if not self.df.empty:
            self._serialize_chunk()

    def _serialize_chunk(self):
        """Serialize the current DataFrame chunk."""
        df_path = f"df_chunk_{self.chunk_flag}_{len(self.df)}.{FEATHER_FORMAT}"
        logger.info(f"Serializing dataframe to {df_path}")
        self.df.reset_index(drop=True).to_feather(df_path)
        self.df = pd.DataFrame(columns=["repo_id", "file_structure", "readme_content", "key_code_snippets"])
        self.chunk_flag += 1

def upload_to_hub(file_format: str, repo_id: str):
    """Upload files to Hugging Face Hub."""
    try:
        create_repo(repo_id=repo_id, exist_ok=True, repo_type="dataset")
        logger.info(f"Repository '{repo_id}' created or already exists")
        
        with tempfile.TemporaryDirectory() as tmpdirname:
            current_dir = os.getcwd()
            
            for file in os.listdir(current_dir):
                if file.endswith(f".{file_format}"):
                    src_path = os.path.join(current_dir, file)
                    dest_path = os.path.join(tmpdirname, file)
                    shutil.move(src_path, dest_path)
            
            upload_folder(repo_id=repo_id, folder_path=tmpdirname, repo_type="dataset")
            logger.info(f"Uploaded '{file_format}' files to '{repo_id}'")
            
    except Exception as e:
        logger.error(f"Error in upload_to_hub: {e}")

if __name__ == "__main__":
    try:
        processor = RepoProcessor(MIRROR_DIRECTORY)
        processor.process_repositories()
        
        logger.info("Uploading processed data to Hub")
        upload_to_hub(file_format=FEATHER_FORMAT, repo_id=DATASET_ID)
        
        logger.info("Processing completed successfully")
    except Exception as e:
        logger.error(f"Fatal error in main execution: {e}")