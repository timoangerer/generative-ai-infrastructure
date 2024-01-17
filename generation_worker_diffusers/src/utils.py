
from pathlib import Path

def get_model_path_by_name(model_name, models_dir):
    models_dir_path = Path(models_dir)
    
    if not models_dir_path.is_dir():
        raise NotADirectoryError(f"The path {models_dir} is not a valid directory.")
    
    for item in models_dir_path.iterdir():
        if item.is_file() and item.stem == model_name:
            return str(item.resolve())
    
    return None