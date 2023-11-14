import requests
import io
import base64
import os
from PIL import Image
import datetime


class Txt2ImgGenerationOverrideSettings():
    def __init__(self, sd_model_checkpoint: str):
        self.sd_model_checkpoint = sd_model_checkpoint

    def to_dict(self) -> dict:
        return {
            'sd_model_checkpoint': self.sd_model_checkpoint
        }

    @staticmethod
    def from_dict(data: dict):
        return Txt2ImgGenerationOverrideSettings(
            sd_model_checkpoint=data['sd_model_checkpoint']
        )


class Txt2ImgGenerationSettings():
    def __init__(self, prompt: str, negative_prompt: str, styles: list[str], seed: int, sampler_name: str, batch_size: int, n_iters: int, steps: int, cfg_scale: float, width: int, height: int, override_settings: Txt2ImgGenerationOverrideSettings):
        self.prompt = prompt
        self.negative_prompt = negative_prompt
        self.styles = styles
        self.seed = seed
        self.sampler_name = sampler_name
        self.batch_size = batch_size
        self.n_iters = n_iters
        self.steps = steps
        self.cfg_scale = cfg_scale
        self.width = width
        self.height = height
        self.override_settings = override_settings

    def to_dict(self) -> dict:
        return {
            'prompt': self.prompt,
            'negative_prompt': self.negative_prompt,
            'styles': self.styles,
            'seed': self.seed,
            'sampler_name': self.sampler_name,
            'batch_size': self.batch_size,
            'n_iters': self.n_iters,
            'steps': self.steps,
            'cfg_scale': self.cfg_scale,
            'width': self.width,
            'height': self.height,
            'override_settings': self.override_settings.to_dict()
        }

    @staticmethod
    def from_dict(data: dict):
        return Txt2ImgGenerationSettings(
            prompt=data['prompt'],
            negative_prompt=data['negative_prompt'],
            styles=data['styles'],
            seed=data['seed'],
            sampler_name=data['sampler_name'],
            batch_size=data['batch_size'],
            n_iters=data['n_iters'],
            steps=data['steps'],
            cfg_scale=data['cfg_scale'],
            width=data['width'],
            height=data['height'],
            override_settings=Txt2ImgGenerationOverrideSettings.from_dict(
                data['override_settings'])
        )


class GenerateTxt2ImgError(Exception):
    pass


def generate_txt2img(sd_server_url: str, generation_settings: Txt2ImgGenerationSettings) -> Image.Image:
    response = None
    try:
        response = requests.post(
            url=f'{sd_server_url}/sdapi/v1/txt2img', json=generation_settings.to_dict(), timeout=None)
        response.raise_for_status()

        raw_image = response.json().get("images")[0]

        image = Image.open(io.BytesIO(
            base64.b64decode(raw_image.split(",", 1)[0])))

        return image
    except requests.exceptions.HTTPError as err:
        error_message = "An error occured trying to generate txt2img."
        if response is not None:
            error_message += f" Response Text: {response.text}"
        raise GenerateTxt2ImgError(error_message) from err
    except Exception as e:
        raise GenerateTxt2ImgError(e) from e


def save_image_locally(image):
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    image.save(
        output_dir + f'/output-{datetime.datetime.now().isoformat()}.png')
