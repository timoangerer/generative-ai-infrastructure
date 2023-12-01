import json
import os
from pathlib import Path


class ModelNotFoundException(Exception):
    """Exception raised when the model is not found."""
    pass


class JsonFileNotFoundException(Exception):
    """Exception raised when the JSON file is not found."""
    pass


def get_model_path_by_name(model_name, json_file='models.json', root_folder: Path = Path('models')):
    """Get the absolute model path by its name."""
    json_file_path = os.path.join(root_folder, json_file)
    try:
        with open(json_file_path, 'r') as file:
            models = json.load(file)
            for model in models:
                if model['name'] == model_name:
                    return os.path.abspath(os.path.join(root_folder, model['path']))
            raise ModelNotFoundException(
                f"Model with name '{model_name}' not found.")
    except FileNotFoundError:
        raise JsonFileNotFoundException(f"File {json_file_path} not found.")


def get_model_path_by_hash(model_hash, json_file='models.json', root_folder: Path = Path('models')):
    """Get the absolute model path by its hash."""
    json_file_path = os.path.join(root_folder, json_file)
    try:
        with open(json_file_path, 'r') as file:
            models = json.load(file)
            for model in models:
                if model['hash'] == model_hash:
                    return os.path.abspath(os.path.join(root_folder, model['path']))
            raise ModelNotFoundException(
                f"Model with hash '{model_hash}' not found.")
    except FileNotFoundError:
        raise JsonFileNotFoundException(f"File {json_file_path} not found.")
