from dataclasses import dataclass
import io

import rpyc
from PIL import Image

from sd_generation import Txt2ImgGenerationSettings

# Shape of the request has to be the same as in the server
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
    model_name: str

def generate_txt2img_diffusers_rpc(settings: Txt2ImgGenerationRequest):
    conn = rpyc.connect("localhost", 18812, config={
    'allow_public_attrs': True, "sync_request_timeout": 240})
    remote_service = conn.root

    img_byte_arr = remote_service.generate_txt2img(settings)
    image = Image.open(io.BytesIO(img_byte_arr))

    conn.close()

    return image

def generate_txt2img_diffusers(settings: Txt2ImgGenerationSettings) -> Image.Image:
    request = Txt2ImgGenerationRequest(
        prompt=settings.prompt,
        negative_prompt=settings.negative_prompt,
        width=settings.width,
        height=settings.height,
        guidance_scale=settings.cfg_scale,
        num_inference_steps=settings.steps,
        sampler_name=settings.sampler_name,
        seed=settings.seed,
        model_name="v1-5-pruned-emaonly"
    )

    img = generate_txt2img_diffusers_rpc(request)
    return img