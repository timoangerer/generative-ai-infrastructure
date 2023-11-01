from typing import List, Optional
from uuid import UUID
from config import Config

from models import Txt2ImgGenerationOverrideSettings, Txt2ImgGenerationSettings, Txt2ImgImgDTO

from trino.dbapi import connect

config = Config()

conn = connect(
    host=config.trino_host,
    port=config.trino_port,
    user="<username>",
    catalog='pulsar',
    schema='public/default'
)


def close_trino_connection():
    conn.close()


def map_row_to_image(row):
    id, metadata, gs, request_time, complete_time, s3_bucket, s3_object_key = row

    generation_settings = Txt2ImgGenerationSettings(
        prompt=gs.prompt,
        negative_prompt=gs.negative_prompt,
        styles=gs.styles,
        seed=gs.seed,
        sampler_name=gs.sampler_name,
        batch_size=gs.batch_size,
        n_iters=gs.n_iters,
        steps=gs.steps,
        cfg_scale=gs.cfg_scale,
        width=gs.width,
        height=gs.height,
        override_settings=Txt2ImgGenerationOverrideSettings(
            sd_model_checkpoint=gs.override_settings[0]
        )
    )

    if s3_bucket is None or s3_object_key is None:
        image_url = None
    else:
        image_url = f"https://{s3_bucket}.s3.amazonaws.com/{s3_object_key}"

    return Txt2ImgImgDTO(
        id=id,
        metadata=metadata,
        request_time=request_time,
        complete_time=complete_time,
        generation_settings=generation_settings,
        image_url=image_url
    )


def get_all_images(offset: int, limit: int) -> List[Txt2ImgImgDTO]:
    cursor = conn.cursor()

    sql = """
        select
            req.id,
            req.metadata,
            req.generation_settings,
            req.__publish_time__ as request_time,
            comp.__publish_time__ as complete_time,
            comp.s3_bucket,
            comp.s3_object_key
        from
            requested_txt2img_generation as req
        left join completed_txt2img_generation as comp on
            req.id = comp.id
        order by request_time
        offset ?
        limit ?
    """
    cursor.execute(sql, (offset, limit))
    rows = cursor.fetchall()

    images = [map_row_to_image(row) for row in rows]

    conn.close()
    return images


def get_image_by_id(id: UUID) -> Optional[Txt2ImgImgDTO]:
    cursor = conn.cursor()

    sql = """
        select
            req.id,
            req.metadata,
            req.generation_settings,
            req.__publish_time__ as request_time,
            comp.__publish_time__ as complete_time,
            comp.s3_bucket,
            comp.s3_object_key
        from
            requested_txt2img_generation as req
        left join completed_txt2img_generation as comp on
            req.id = comp.id
        where req.id = ?
    """
    cursor.execute(sql, (str(id),))
    rows = cursor.fetchall()

    conn.close()

    if len(rows) == 0:
        return None
    elif len(rows) > 1:
        raise Exception("More than one image found with the same id")

    return map_row_to_image(rows[0])
