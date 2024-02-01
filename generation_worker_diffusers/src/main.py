from dataclasses import dataclass
import io
import logging
import sys
import time
import rpyc
from rpyc.utils.server import ThreadedServer
from PIL import Image
from src.settings import get_settings
from src.stable_diffusion import (GenerationSettings, create_pipeline,
                                  generate_text2image, select_device)
from src.utils import get_model_path_by_name

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

settings = get_settings()


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


def img_to_byte_array(img: Image.Image):
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    return img_byte_arr

class MyService(rpyc.Service):
    def exposed_health_check(self):
        logger.info("Health check")
        return "OK"

    def exposed_generate_txt2img(self, request: Txt2ImgGenerationRequest, iter_duration_callback):      
        models_dir = settings.models_dir
        model_path = get_model_path_by_name(
            model_name=request.model, models_dir=models_dir)
        if model_path is None:
            raise Exception(f'Model "{request.model}" not found')

        generation_settings = GenerationSettings(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            width=request.width,
            height=request.height,
            guidance_scale=request.guidance_scale,
            num_inference_steps=request.num_inference_steps,
            sampler_name=request.sampler_name,
            seed=request.seed
        )

        pipeline = create_pipeline(model_path=model_path)

        curr_start = time.time_ns()
        def generation_progress_callback(self, step: int, timestep: int, callback_kwargs: dict):
            nonlocal curr_start
            start = curr_start
            end = time.time_ns()

            iter_duration_callback(start, end, step)

            curr_start = end
            return callback_kwargs

        img = generate_text2image(
            settings=generation_settings, pipeline=pipeline, callback_on_step_end=generation_progress_callback)

        img_byte_arr = img_to_byte_array(img)
        return img_byte_arr


if __name__ == "__main__":
    server = ThreadedServer(MyService, port=18812, protocol_config={
        'allow_public_attrs': True,
    })
    logger.info("Starting RPC server")
    server.start()
