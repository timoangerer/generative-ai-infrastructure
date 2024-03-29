import logging
from dataclasses import dataclass
from os import PathLike
from typing import Callable, Optional, Union
import sys

import torch
from diffusers.pipelines.stable_diffusion.pipeline_stable_diffusion import \
    StableDiffusionPipeline
from PIL import Image

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)


@dataclass
class GenerationSettings:
    prompt: str
    negative_prompt: str
    width: int
    height: int
    guidance_scale: float
    num_inference_steps: int
    sampler_name: str
    seed: int


def select_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    elif torch.backends.mps.is_built():
        return torch.device("mps")
    else:
        return torch.device("cpu")


def create_pipeline(model_path: Optional[Union[str, PathLike]]):
    device = select_device()
    logger.info(f"Creating pipeline for {model_path}")
    logger.info(f"Using device: {device}")

    torch_dtype = torch.float32
    if device == torch.device("cuda"):
        torch_dtype = torch.float16

    pipeline = StableDiffusionPipeline.from_single_file(
        pretrained_model_link_or_path=model_path,
        safety_checker=None,
        requires_safety_checker=False,
        torch_dtype=torch_dtype,
        local_files_only=True,
        use_safetensores=True
    )

    pipeline.to(device)

    return pipeline


def generate_text2image(settings: GenerationSettings,
                        pipeline,
                        callback_on_step_end: Optional[Callable] = None) -> Image.Image:

    device = select_device()
    generator = torch.Generator(device=device).manual_seed(settings.seed)

    image = pipeline(
        generator=generator,
        prompt=settings.prompt,
        negative_prompt=settings.negative_prompt,
        num_inference_steps=settings.num_inference_steps,
        height=settings.height,
        width=settings.width,
        guidance_scale=settings.guidance_scale,
        callback_on_step_end=callback_on_step_end
    ).images[0]

    return image
