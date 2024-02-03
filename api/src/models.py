import random
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class Txt2ImgGenerationSettings(BaseModel):
    prompt: str
    negative_prompt: str = ""
    seed: int = Field(default=random.randint(0, 9999999999), ge=0)
    sampler_name: str = Field(min_length=1)
    batch_size: int = 1
    n_iters: int = 1
    steps: int = 20
    cfg_scale: float = 7
    width: int = 512
    height: int = 512
    model: str


class Txt2ImgGenerationRequest(BaseModel):
    id: UUID
    metadata: dict[str, str]
    generation_settings: Txt2ImgGenerationSettings


class Txt2ImgGenerationRequestDTO(BaseModel):
    metadata: dict[str, str]
    generation_settings: Txt2ImgGenerationSettings

class Txt2ImgGenerationResponseDTO(BaseModel):
    message: str
    id: UUID

class Txt2ImgImgDTO(BaseModel):
    id: UUID
    metadata: dict[str, str]
    request_time: datetime
    complete_time: Optional[datetime]
    generation_settings: Txt2ImgGenerationSettings
    image_url: Optional[str]