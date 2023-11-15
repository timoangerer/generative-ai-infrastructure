import random
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class Txt2ImgGenerationOverrideSettings(BaseModel):
    sd_model_checkpoint: str = Field(..., min_length=1)


class Txt2ImgGenerationSettings(BaseModel):
    prompt: str
    negative_prompt: str = ""
    styles: List[str] = []
    seed: int = Field(default=random.randint(0, 9999999999), ge=0)
    sampler_name: str = Field(default="DPM++ 2M Karras", min_length=1)
    batch_size: int = 1
    n_iters: int = 1
    steps: int = 20
    cfg_scale: float = 7
    width: int = 512
    height: int = 512
    override_settings: Txt2ImgGenerationOverrideSettings


class Txt2ImgGenerationRequest(BaseModel):
    id: UUID
    metadata: dict[str, str]
    generation_settings: Txt2ImgGenerationSettings


class Txt2ImgGenerationRequestDTO(BaseModel):
    metadata: dict[str, str]
    generation_settings: Txt2ImgGenerationSettings


class Txt2ImgImgDTO(BaseModel):
    id: UUID
    metadata: dict[str, str]
    request_time: datetime
    complete_time: Optional[datetime]
    generation_settings: Txt2ImgGenerationSettings
    image_url: Optional[str]
