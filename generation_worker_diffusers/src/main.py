import datetime

from src.settings import get_settings
from src.stable_diffusion import GenerationSettings, generate_text2image
from src.utils import get_model_path_by_name

settings = get_settings()

models_path = settings.models_path

model_path = get_model_path_by_name(
    model_name="v1-5-pruned-emaonly", root_folder=models_path, json_file="models.json")

settings = GenerationSettings(
    prompt="A painting of a cat",
    negative_prompt="",
    width=512,
    height=512,
    guidance_scale=7.5,
    num_inference_steps=5,
    sampler_name="ddim",
)

img = generate_text2image(settings=settings, model_path=model_path)


current_time = datetime.datetime.now().isoformat()
file_name = f"output/{current_time}.png"
img.save(file_name)
