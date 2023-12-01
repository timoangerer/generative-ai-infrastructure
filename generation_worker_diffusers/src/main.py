from dataclasses import dataclass

import rpyc
from rpyc.utils.server import ThreadedServer

from src.settings import get_settings
from src.stable_diffusion import (GenerationSettings, create_pipeline,
                                  generate_text2image)
from src.utils import get_model_path_by_name

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
    model_name: str


class MyService(rpyc.Service):
    def exposed_generate_txt2img(self, request: Txt2ImgGenerationRequest):
        models_path = settings.models_path

        model_path = get_model_path_by_name(
            model_name=request.model_name, root_folder=models_path, json_file="models.json")

        def generation_progress_callback(self, step: int, timestep: int, callback_kwargs: dict):
            print(f"Step: {step}, Timestep: {timestep}")
            return callback_kwargs

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

        img = generate_text2image(
            settings=generation_settings, pipeline=pipeline, callback_on_step_end=generation_progress_callback)

        return img


if __name__ == "__main__":
    server = ThreadedServer(MyService, port=18812, protocol_config={
        'allow_public_attrs': True,
    })
    print("### Starting RPC server")
    server.start()
