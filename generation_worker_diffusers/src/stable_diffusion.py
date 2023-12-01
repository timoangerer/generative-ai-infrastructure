from dataclasses import dataclass
from os import PathLike
from typing import Optional, Union

import torch
from diffusers.pipelines.stable_diffusion.pipeline_stable_diffusion import \
    StableDiffusionPipeline
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


def select_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    elif torch.backends.mps.is_built():
        return torch.device("mps")
    else:
        return torch.device("cpu")


def generate_text2image(settings: GenerationSettings, model_path: Optional[Union[str, PathLike]]) -> Image.Image:
    device = select_device()

    # Load the pipeline for the specified device and dtype
    pipeline = StableDiffusionPipeline.from_single_file(
        pretrained_model_link_or_path=model_path,
        safety_checker=None
    ).to(device)

    image = pipeline(
        prompt=settings.prompt,
        negative_prompt=settings.negative_prompt,
        num_inference_steps=settings.num_inference_steps,
        height=settings.height,
        width=settings.width,
        guidance_scale=settings.guidance_scale,
    ).images[0]

    return image
