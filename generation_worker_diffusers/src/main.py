from src.utils import get_model_path_by_name
import os

models_root_path = os.environ.get('MODELS_PATH')

model_path = get_model_path_by_name(model_name="v1-5-pruned-emaonly", root_folder=models_root_path, json_file="models.json")

print(model_path)
