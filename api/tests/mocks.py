from faker import Faker
import random
from uuid import uuid4

from models import Txt2ImgGenerationOverrideSettings, Txt2ImgGenerationSettings, Txt2ImgImgDTO

fake = Faker()


def mock_txt2img_generation_override_settings():
    return Txt2ImgGenerationOverrideSettings(
        sd_model_checkpoint=fake.file_name()
    )


def mock_txt2img_generation_settings():
    return Txt2ImgGenerationSettings(
        prompt=fake.sentence(),
        negative_prompt=fake.sentence(),
        styles=[fake.word() for _ in range(random.randint(1, 5))],
        seed=random.randint(0, 1000),
        sampler_name=fake.word(),
        batch_size=random.randint(1, 100),
        n_iters=random.randint(1, 100),
        steps=random.randint(1, 10),
        cfg_scale=random.uniform(0.5, 1.5),
        width=random.randint(64, 1920),
        height=random.randint(64, 1080),
        override_settings=mock_txt2img_generation_override_settings()
    )


def mock_txt2img_img_dto():
    return Txt2ImgImgDTO(
        id=uuid4(),   # Use uuid4() here
        metadata={fake.word(): fake.word()
                  for _ in range(random.randint(1, 5))},
        request_time=fake.date_time_this_decade(),
        complete_time=fake.date_time_this_decade() if fake.boolean(
            chance_of_getting_true=75) else None,
        generation_settings=mock_txt2img_generation_settings(),
        image_url=fake.image_url() if fake.boolean(chance_of_getting_true=75) else None
    )
