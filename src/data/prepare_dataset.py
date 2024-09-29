import os
import pandas as pd
from nbformat import reads, NO_CONVERT
from tqdm import tqdm
from datasets import Dataset
from typing import Dict
from huggingface_hub import create_repo, upload_folder
import tempfile
import shutil  # Use shutil for file operations

# Constants
MIRROR_DIRECTORY = "test"
DATASET_ID = "hamza-amin/readme-gen-data"
SERIALIZE_IN_CHUNKS = 10000
FEATHER_FORMAT = "ftr"

# Block the following formats.
IMAGE = ["png", "jpg", "jpeg", "gif"]
VIDEO = ["mp4", "jfif"]
DOC = [
    "key",
    "PDF",
    "pdf",
    "docx",
    "xlsx",
    "pptx",
]
AUDIO = ["flac", "ogg", "mid", "webm", "wav", "mp3"]
ARCHIVE = ["jar", "aar", "gz", "zip", "bz2"]
MODEL = ["onnx", "pickle", "model", "neuron"]
OTHERS = [
    "npy",
    "index",
    "inv",
    "DS_Store",
    "rdb",
    "pack",
    "idx",
    "glb",
    "gltf",
    "len",
    "otf",
    "unitypackage",
    "ttf",
    "xz",
    "pcm",
    "opus",
]
ANTI_FORMATS = tuple(IMAGE + VIDEO + DOC + AUDIO + ARCHIVE + OTHERS)


def upload_to_hub(file_format: str, repo_id: str):
    """Moves all the files matching `file_format` to a folder and
    uploads the folder to the Hugging Face Hub."""
    try:
        # Create the repository on Hugging Face Hub
        repo = create_repo(repo_id=repo_id, exist_ok=True, repo_type="dataset")
        print(f"Repository '{repo_id}' created or already exists.")
    except Exception as e:
        print(f"Failed to create repository: {e}")
        return  # Exit the function if repository creation fails

    # Create a temporary directory to store the files
    with tempfile.TemporaryDirectory() as tmpdirname:
        print(f"Created temporary directory: {tmpdirname}")

        # Get the current working directory
        current_dir = os.getcwd()

        # Iterate over all files in the current directory
        for file in os.listdir(current_dir):
            if file.endswith(f".{file_format}"):
                src_path = os.path.join(current_dir, file)
                dest_path = os.path.join(tmpdirname, file)
                try:
                    shutil.move(src_path, dest_path)
                    print(f"Moved '{file}' to temporary directory.")
                except Exception as e:
                    print(f"Error moving '{file}': {e}")

        # Upload the folder to Hugging Face Hub
        try:
            upload_folder(repo_id=repo_id, folder_path=tmpdirname, repo_type="dataset")
            print(f"Uploaded '{file_format}' files to the Hub under repository '{repo_id}'.")
        except Exception as e:
            print(f"Failed to upload folder to Hugging Face Hub: {e}")
            return  # Exit if upload fails

    print(f"All '{file_format}' files successfully uploaded to '{repo_id}'.")



def filter_code_cell(cell) -> bool:
    """Filters a code cell w.r.t shell commands, etc."""
    only_shell = cell["source"].startswith("!")
    only_magic = "%%capture" in cell["source"]
    return not (only_shell or only_magic)


def process_file(directory_name: str, file_path: str) -> Dict[str, str]:
    """Processes a single file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            if file_path.endswith("ipynb"):
                # Process Jupyter Notebook files
                code_cell_str = ""
                notebook = reads(content, NO_CONVERT)

                code_cells = [
                    c
                    for c in notebook["cells"]
                    if c["cell_type"] == "code" and filter_code_cell(c)
                ]

                for cell in code_cells:
                    code_cell_str += cell["source"]
                content = code_cell_str
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        content = ""

    return {
        "repo_id": directory_name,
        "file_path": file_path,
        "content": content,
    }


def read_repository_files(directory) -> pd.DataFrame:
    """Reads the files from the locally cloned repositories."""
    file_paths = []
    df = pd.DataFrame(columns=["repo_id", "file_path", "content"])
    chunk_flag = 0

    # Recursively find all files within the directory
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if not file_path.endswith(ANTI_FORMATS) and all(
                k not in file_path for k in [".git", "__pycache__", "xcodeproj"]
            ):
                file_paths.append((os.path.basename(root), file_path))

    # Process files sequentially.
    print(f"Total file paths: {len(file_paths)}.")
    print("Reading file contents...")

    for i, (directory_name, file_path) in enumerate(tqdm(file_paths, desc="Processing files")):
        file_content = process_file(directory_name, file_path)

        if file_content["content"]:
            temp_df = pd.DataFrame.from_dict([file_content])
            df = pd.concat([df, temp_df], ignore_index=True)

            if SERIALIZE_IN_CHUNKS and len(df) >= SERIALIZE_IN_CHUNKS:
                df_path = f"df_chunk_{chunk_flag}_{len(df)}.{FEATHER_FORMAT}"
                print(f"Serializing dataframe to {df_path}...")
                df.reset_index(drop=True).to_feather(df_path)
                df = pd.DataFrame(columns=["repo_id", "file_path", "content"])
                chunk_flag += 1

    # Serialize any remaining data
    if not df.empty:
        df_path = f"df_chunk_{chunk_flag}_{len(df)}.{FEATHER_FORMAT}"
        print(f"Serializing remaining dataframe to {df_path}...")
        df.reset_index(drop=True).to_feather(df_path)

    return df


if __name__ == "__main__":
    df = read_repository_files(MIRROR_DIRECTORY)
    print("DataFrame created, creating dataset...")
    upload_to_hub(file_format=FEATHER_FORMAT, repo_id=DATASET_ID)
    print(f"{FEATHER_FORMAT} files uploaded to the Hub.")
    
    if not SERIALIZE_IN_CHUNKS:
        try:
            dataset = Dataset.from_pandas(df)
            dataset.push_to_hub(DATASET_ID)
            print(f"Dataset '{DATASET_ID}' pushed to the Hub.")
        except Exception as e:
            print(f"Failed to push dataset to the Hub: {e}")
