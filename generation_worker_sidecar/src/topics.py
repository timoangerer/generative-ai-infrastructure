from enum import Enum


class Topics(Enum):
    REQUESTED_TXT2IMG_GENERATION = "requested_txt2img_generation"
    DLQ_REQUESTED_TXT2IMG_GENERATION = "dlq_requested_txt2img_generation"
    COMPLETED_TXT2IMG_GENERATION = "completed_txt2img_generation"
