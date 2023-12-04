import argparse
import os
import shutil
from typing import List
from huggingface_hub import snapshot_download

def valid_path(path):
    # Convert relative path to absolute path
    path = os.path.abspath(path)

    if not os.path.isabs(path):
        raise argparse.ArgumentTypeError(f"'{path}' is not a valid absolute path.")
    return path

def download_models(hf_home: str, repo_ids: List[str]):
    hf_cache = os.path.join(hf_home, "hub")

    # Check if the directory exists, and if so, delete it
    if os.path.exists(hf_cache):
        shutil.rmtree(hf_cache)

    os.makedirs(hf_cache)

    allow_patterns = ["*.json","*.txt", "*.bin"]
    for repo_id in repo_ids:
        snapshot_download(repo_id=repo_id, cache_dir=hf_cache, allow_patterns=allow_patterns)

def main():
    parser = argparse.ArgumentParser(description="Download models from Hugging Face Hub")
    parser.add_argument("hf_home", type=valid_path, help="Path to the Hugging Face home directory")

    args = parser.parse_args()

    repo_ids = ["openai/clip-vit-large-patch14", "CompVis/stable-diffusion-safety-checker"]

    download_models(args.hf_home, repo_ids)

if __name__ == "__main__":
    main()
