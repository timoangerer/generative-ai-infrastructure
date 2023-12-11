from dataclasses import dataclass

import rpyc
from PIL import Image


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


def generate_txt2img_diffusers(settings: Txt2ImgGenerationRequest):
    conn = rpyc.connect("localhost", 18812, config={
        'allow_public_attrs': True, "sync_request_timeout": 240})
    remote_service = conn.root
    
    result: Image.Image = remote_service.generate_txt2img(settings)
    print(f"The result is: {result.size}")

    conn.close()


def main():
    request = Txt2ImgGenerationRequest(
        prompt="A painting of a cat",
        negative_prompt="",
        width=512,
        height=512,
        guidance_scale=7.5,
        num_inference_steps=5,
        sampler_name="ddim",
        seed=42,
        model_name="v1-5-pruned-emaonly"
    )

    generate_txt2img_diffusers(request)


if __name__ == "__main__":
    main()
