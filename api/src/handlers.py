from typing import List
from uuid import UUID

from models import Txt2ImgImgDTO, Txt2ImgGenerationRequest
from pulsar_utils import send_generation_request
import repository as TrinoRepository


def get_all_images(offset: int, limit: int) -> List[Txt2ImgImgDTO]:
    return TrinoRepository.get_all_images(offset=offset, limit=limit)


def get_image_by_id(id: UUID) -> Txt2ImgImgDTO:
    return TrinoRepository.get_image_by_id(id)


def generate_image(generation_request: Txt2ImgGenerationRequest) -> UUID:
    send_generation_request(generation_request)
