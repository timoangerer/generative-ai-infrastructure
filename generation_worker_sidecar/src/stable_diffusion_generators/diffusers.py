from dataclasses import dataclass
import io

import rpyc
from PIL import Image
from stable_diffusion_generators.abstract_stable_diffusion_generator import AbstractStableDiffusionGenerator

from models import Txt2ImgGenerationSettings


@dataclass
class Txt2ImgGenerationRequest:
    prompt: str
    negative_prompt: str
    width: int
    height: int
    guidance_scale: float
    num_inference_steps: int
    sampler_name: str
    seed: int
    model: str


class DiffusersStableDiffusionGenerator(AbstractStableDiffusionGenerator):
    def __init__(self):
        self.conn = None

    def _get_connection(self):
        if self.conn is None or self.conn.closed:
            self.conn = rpyc.connect("localhost", 18812, config={
                                     'allow_public_attrs': True, "sync_request_timeout": 240})
        return self.conn.root

    def generate_txt2img(self, settings: Txt2ImgGenerationSettings, iter_duration_callback) -> Image.Image:
        request = Txt2ImgGenerationRequest(
            prompt=settings.prompt,
            negative_prompt=settings.negative_prompt,
            width=settings.width,
            height=settings.height,
            guidance_scale=settings.cfg_scale,
            num_inference_steps=settings.steps,
            sampler_name=settings.sampler_name,
            seed=settings.seed,
            model=settings.model
        )

        conn = rpyc.connect("localhost", 18812, config={
            'allow_public_attrs': True, "sync_request_timeout": 240})
        remote_service = conn.root

        img_byte_arr = remote_service.generate_txt2img(
            request, iter_duration_callback)
        image = Image.open(io.BytesIO(img_byte_arr))

        conn.close()

        return image

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.conn.close()
