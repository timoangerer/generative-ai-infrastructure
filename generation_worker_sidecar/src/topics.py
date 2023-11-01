from enum import Enum


class Topics(Enum):
    REQUESTED_TXT2IMG_GENERATION = "requested_txt2img_generation"
    COMPLETED_TXT2IMG_GENERATION = "completed_txt2img_generation"
    STARTED_TXT2IMG_GENERATION = "started_txt2img_generation"
