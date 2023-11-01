from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class Txt2ImgGenerationOverrideSettings(BaseModel):
    sd_model_checkpoint: str


class Txt2ImgGenerationSettings(BaseModel):
    prompt: str
    negative_prompt: str
    styles: List[str]
    seed: int
    sampler_name: str
    batch_size: int
    n_iters: int
    steps: int
    cfg_scale: float
    width: int
    height: int
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
