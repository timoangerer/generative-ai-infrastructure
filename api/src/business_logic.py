from typing import List, Optional
from uuid import UUID

import repository as TrinoRepository
from config import get_config
from models import Txt2ImgGenerationRequest, Txt2ImgImgDTO
from pulsar_utils import send_generation_request
from repository import Repository, TrinoRepository

config = get_config()

repository: Repository = TrinoRepository(
    host=config.trino_host,
    port=config.trino_port,
    user=config.trino_user,
    catalog=config.trino_catalog,
    schema=config.trino_schema
)


def get_all_images(offset: int, limit: int) -> List[Txt2ImgImgDTO]:
    return repository.get_all_images(offset=offset, limit=limit)


def get_image_by_id(id: UUID) -> Optional[Txt2ImgImgDTO]:
    return repository.get_image_by_id(id)


def generate_image(generation_request: Txt2ImgGenerationRequest):
    send_generation_request(generation_request)
