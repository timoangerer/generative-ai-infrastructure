from abc import ABC, abstractmethod
from PIL import Image
from models import Txt2ImgGenerationSettings

class AbstractStableDiffusionGenerator(ABC):
    
    @abstractmethod
    def generate_txt2img(self, settings: Txt2ImgGenerationSettings, iter_duration_callback) -> Image.Image:
        pass
