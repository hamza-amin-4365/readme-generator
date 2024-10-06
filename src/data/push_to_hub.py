from huggingface_hub import hf_hub_download
from datasets import Dataset, load_dataset
from tqdm import tqdm
import pandas as pd
import os
import tempfile
import logging
import shutil

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
SOURCE_REPO = "hamza-amin/readme-gen-data"
TARGET_REPO = "hamza-amin/readme-gen-data-v2"
FILES_TO_PROCESS = [
    "df_chunk_0_173.ftr"
]

def safe_download_file(repo_id: str, filename: str) -> str:
    """Safely download a file from the hub."""
    try:
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        
        # Download the file
        local_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            repo_type="dataset",
            local_dir=temp_dir,
        )
        
        # Create a new temporary file and copy the content
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.ftr')
        shutil.copy2(local_path, temp_file.name)
        
        # Clean up the original temporary directory
        shutil.rmtree(temp_dir)
        
        return temp_file.name
    except Exception as e:
        logger.error(f"Error downloading {filename}: {str(e)}")
        return None

def process_files(files_to_process: list) -> pd.DataFrame:
    """Process specified files and return combined DataFrame."""
    all_dfs = []
    temp_files = []
    
    for filename in tqdm(files_to_process, desc="Processing files"):
        try:
            local_path = safe_download_file(SOURCE_REPO, filename)
            if local_path and os.path.exists(local_path):
                try:
                    df = pd.read_feather(local_path)
                    all_dfs.append(df)
                    temp_files.append(local_path)
                    logger.info(f"Successfully processed {filename} with {len(df)} rows")
                except Exception as e:
                    logger.error(f"Error reading feather file {filename}: {str(e)}")
            else:
                logger.warning(f"Could not download or find {filename}")
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}")
    
    # Clean up temporary files
    for temp_file in temp_files:
        try:
            os.unlink(temp_file)
        except Exception as e:
            logger.warning(f"Error deleting temporary file {temp_file}: {str(e)}")
    
    if not all_dfs:
        logger.error("No files were successfully processed")
        return None
    
    combined_df = pd.concat(all_dfs, ignore_index=True)
    logger.info(f"Combined DataFrame has {len(combined_df)} rows")
    return combined_df

def append_to_existing_dataset(new_df: pd.DataFrame) -> pd.DataFrame:
    """Append new data to existing dataset."""
    try:
        existing_dataset = load_dataset(TARGET_REPO, split="train")
        existing_df = existing_dataset.to_pandas()
        logger.info(f"Existing dataset has {len(existing_df)} rows")
        final_df = pd.concat([existing_df, new_df], ignore_index=True)
        logger.info(f"Combined dataset has {len(final_df)} rows")
        return final_df
    except Exception as e:
        logger.info(f"No existing dataset found, using only new data: {str(e)}")
        return new_df

def save_and_upload_dataset(df: pd.DataFrame, repo_id: str):
    """Save DataFrame as parquet and upload to hub."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        parquet_path = os.path.join(tmpdirname, "data.parquet")
        df.to_parquet(parquet_path)
        
        try:
            dataset = Dataset.from_parquet(parquet_path)
            dataset.push_to_hub(repo_id)
            logger.info(f"Successfully uploaded dataset to {repo_id}")
        except Exception as e:
            logger.error(f"Error uploading to hub: {str(e)}")
            raise

def main():
    try:
        # Process specified files
        new_df = process_files(FILES_TO_PROCESS)
        if new_df is None or len(new_df) == 0:
            logger.error("No data to process. Exiting.")
            return
        
        logger.info(f"Processed {len(new_df)} new rows")
        
        # Append to existing dataset
        final_df = append_to_existing_dataset(new_df)
        
        # Save and upload dataset
        save_and_upload_dataset(final_df, TARGET_REPO)
        
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()