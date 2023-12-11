import hashlib
import json
import os


def compute_hash(filepath):
    """Compute the SHA256 hash of the file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read and update hash in chunks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def find_models(root_folder):
    """Find all model files in the given root folder."""
    models = []
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, root_folder)
            file_hash = compute_hash(file_path)
            models.append({
                "name": os.path.splitext(file)[0],
                # Normalize path for Windows
                "path": relative_path.replace("\\", "/"),
                "hash": file_hash
            })
    return models


def main():
    root_folder = "/home/ubuntu/generative-ai-infrastructure/models"
    models = find_models(root_folder)
    with open("models.json", "w") as json_file:
        json.dump(models, json_file, indent=4)


if __name__ == "__main__":
    main()
