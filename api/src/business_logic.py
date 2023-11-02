from typing import List
from uuid import UUID

import repository as TrinoRepository
from models import Txt2ImgGenerationRequest, Txt2ImgImgDTO
from pulsar_utils import send_generation_request


def get_all_images(offset: int, limit: int) -> List[Txt2ImgImgDTO]:
    return TrinoRepository.get_all_images(offset=offset, limit=limit)


def get_image_by_id(id: UUID) -> Txt2ImgImgDTO:
    return TrinoRepository.get_image_by_id(id)


def generate_image(generation_request: Txt2ImgGenerationRequest):
    send_generation_request(generation_request)
