from dataclasses import dataclass
from os import PathLike
from typing import Optional, Union
from diffusers import StableDiffusionPipeline
import torch
from PIL import Image

@dataclass
class GenerationSettings:
    prompt: str
    negative_prompt: str
    width: int
    height: int
    guidance_scale: float
    num_inference_steps: int
    sampler_name: str


def generate_text2image(settings: GenerationSettings, model_path: Optional[Union[str, PathLike]]) -> Image.Image:
    if torch.cuda.is_available():
        device = "cuda"
        torch_dtype = torch.float16
    else:
        device = "cpu"
        torch_dtype = torch.float32

    # Load the pipeline for the specified device and dtype
    pipeline = StableDiffusionPipeline.from_single_file(
        settings.model_path,
        safety_checker=None
    ).to("mps")

    image = pipeline(
        prompt=settings.prompt,
        # negative_prompt=settings.negative_prompt,
        num_inference_steps=settings.num_inference_steps,
        # height=settings.height,
        # width=settings.width,
        # guidance_scale=settings.guidance_scale,
    ).images[0]

    return image
