from sd_generation import GenerationSettings, generate_text2image, get_model_path_by_name
from pathlib import Path


def test_generate_text2image():
    models_file = Path("models/models.json")
    model_path = get_model_path_by_name(
        "v1-5-pruned-emaonly", json_file=str(models_file.absolute()))

    settings = GenerationSettings(
        prompt="a cat",
        negative_prompt="",
        width=512,
        height=512,
        guidance_scale=7.0,
        num_inference_steps=5,
        sampler_name="sampler_name",
        model_path="/Users/timoangerer/devel/generative-ai-infrastructure/generation_worker_sidecar/models/stable-diffusion/AbyssOrangeMix.safetensors"
    )

    img = generate_text2image(settings)

    img.save("test.png")
