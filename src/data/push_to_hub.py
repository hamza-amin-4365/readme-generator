from huggingface_hub import snapshot_download
from datasets import Dataset
from tqdm import tqdm
import pandas as pd
import glob

REPO_ID = "hamza-amin/readme-gen-data"
FEATHER_FORMAT = "ftr"

if __name__ == "__main__":
    folder_path = snapshot_download(
        repo_id=REPO_ID, allow_patterns="*.ftr", repo_type="dataset"
    )
    
    # Use the correct file pattern to locate all `.ftr` files
    feather_files = glob.glob(f"{folder_path}/*.ftr")
    print("Feather files found:", feather_files)
    
    if not feather_files:
        print("No Feather files found. Please check the path and ensure files are available.")
    else:
        all_dfs = []

        for feather_file in tqdm(feather_files):
            df = pd.read_feather(feather_file)
            all_dfs.append(df)

        final_df = pd.concat(all_dfs)
        print(f"Final DF prepared containing {len(final_df)} rows.")
    
    # Save the DataFrame as a Parquet file
    final_df.to_parquet("final_data.parquet")
    print("Data saved as Parquet format.")

    # Load Parquet into Dataset and push to Hub
    dataset = Dataset.from_parquet("final_data.parquet")
    dataset.push_to_hub("readme-gen-data-v2")
