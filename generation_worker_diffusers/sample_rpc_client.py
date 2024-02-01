from dataclasses import dataclass
import io

import rpyc
from PIL import Image


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


def generate_txt2img_diffusers(settings: Txt2ImgGenerationRequest):
    conn = rpyc.connect("localhost", 18812, config={
        'allow_public_attrs': True, "sync_request_timeout": 240})
    remote_service = conn.root

    def iter_duration_callback(start, end, step):
        print(f"start: {start}, end {end}, i {step}")

    img_byte_arr = remote_service.generate_txt2img(
        settings, iter_duration_callback)
    image = Image.open(io.BytesIO(img_byte_arr))
    print(f"The result is: {image.size}")

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
        model="v1-5-pruned-emaonly"
    )

    generate_txt2img_diffusers(request)


if __name__ == "__main__":
    main()
