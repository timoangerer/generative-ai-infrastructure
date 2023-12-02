import datetime

from src.settings import get_settings
from src.stable_diffusion import GenerationSettings, generate_text2image
from src.utils import get_model_path_by_name


def main():
    models_path = get_settings().models_path

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
        seed=42
    )

    def generation_progress_callback(self, step: int, timestep: int, callback_kwargs: dict):
        print(f"Step: {step}, Timestep: {timestep}")
        return callback_kwargs

    img = generate_text2image(
        settings=settings, model_path=model_path, callback_on_step_end=generation_progress_callback)

    assert img is not None

    current_time = datetime.datetime.now().isoformat()
    file_name = f"{current_time}.png"
    img.save(file_name)


if __name__ == "__main__":
    print("Starting sample generation...")
    main()