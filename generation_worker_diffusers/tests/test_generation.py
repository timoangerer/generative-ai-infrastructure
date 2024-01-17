# import datetime
# from pathlib import Path

# from src.stable_diffusion import GenerationSettings, generate_text2image
# from src.utils import get_model_path_by_name


# def test_generate_text2image():
#     models_folder= Path('./models')

#     model_path = get_model_path_by_name(
#         model_name="v1-5-pruned-emaonly", models_folder=models_folder)

#     settings = GenerationSettings(
#         prompt="A painting of a cat",
#         negative_prompt="",
#         width=512,
#         height=512,
#         guidance_scale=7.5,
#         num_inference_steps=5,
#         sampler_name="ddim",
#         seed=42
#     )

#     def generation_progress_callback(self, step: int, timestep: int, callback_kwargs: dict):
#         print(f"Step: {step}, Timestep: {timestep}")
#         return callback_kwargs

#     img = generate_text2image(
#         settings=settings, model_path=model_path, callback_on_step_end=generation_progress_callback)

#     assert img is not None

#     current_time = datetime.datetime.now().isoformat()
#     file_name = f"output/{current_time}.png"
#     img.save(file_name)
