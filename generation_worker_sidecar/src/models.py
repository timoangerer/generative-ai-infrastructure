from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Txt2ImgGenerationSettings:
    prompt: str
    negative_prompt: str
    seed: int
    sampler_name: str
    batch_size: int
    n_iters: int
    steps: int
    cfg_scale: float
    width: int
    height: int
    model: str


@dataclass
class RequestedTxt2ImgGenerationEvent:
    id: str
    generation_settings: Txt2ImgGenerationSettings
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class CompletedTxt2ImgGenerationEvent:
    id: str
    object_url: str
    metadata: Dict[str, str] = field(default_factory=dict)
