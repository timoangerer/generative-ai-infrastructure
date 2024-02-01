import logging
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from opentelemetry import trace
from trino.dbapi import connect

from models import (Txt2ImgGenerationSettings, Txt2ImgImgDTO)

tracer = trace.get_tracer(__name__)


class DBError(Exception):
    """General database error."""


class ImageNotFound(DBError):
    """Image not found."""


class Repository(ABC):

    @abstractmethod
    def get_all_images(self, offset: int, limit: int) -> List[Txt2ImgImgDTO]:
        pass

    @abstractmethod
    def get_image_by_id(self, id: UUID) -> Txt2ImgImgDTO:
        pass


class TrinoRepository(Repository):
    logger = logging.getLogger(__name__)

    def __init__(self, host: str, port: int, user: str, catalog: str = 'pulsar', schema: str = 'public/default'):
        self.host = host
        self.port = port
        self.user = user
        self.catalog = catalog
        self.schema = schema
        self.logger = logging.getLogger(__name__)

    def get_connection(self):
        return connect(
            host=self.host,
            port=self.port,
            user=self.user,
            catalog=self.catalog,
            schema=self.schema
        )

    def map_row_to_image(self, row):
        id, metadata, gs, request_time, complete_time, image_url = row

        generation_settings = Txt2ImgGenerationSettings(
            prompt=gs.prompt,
            negative_prompt=gs.negative_prompt,
            seed=gs.seed,
            sampler_name=gs.sampler_name,
            batch_size=gs.batch_size,
            n_iters=gs.n_iters,
            steps=gs.steps,
            cfg_scale=gs.cfg_scale,
            width=gs.width,
            height=gs.height,
            model=gs.model
        )

        return Txt2ImgImgDTO(
            id=id,
            metadata=metadata,
            request_time=request_time,
            complete_time=complete_time,
            generation_settings=generation_settings,
            image_url=image_url
        )

    @tracer.start_as_current_span("get_all_images")
    def get_all_images(self, offset: int, limit: int) -> List[Txt2ImgImgDTO]:
        try:
            with self.get_connection() as conn:
                conn.legacy_prepared_statements = True  # TODO: remove this in prod
                cursor = conn.cursor()

                sql = """
                    select
                        req.id,
                        req.metadata,
                        req.generation_settings,
                        req.__publish_time__ as request_time,
                        comp.__publish_time__ as complete_time,
                        comp.image_url
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

                images = [self.map_row_to_image(row) for row in rows]

                cursor.close()
                return images

        except Exception as e:
            self.logger.error(f"Error while fetching images: {e}")
            raise DBError(
                "An error occurred while fetching images.") from e

    @tracer.start_as_current_span("get_image_by_id")
    def get_image_by_id(self, id: UUID) -> Optional[Txt2ImgImgDTO]:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            sql = """
                select
                    req.id,
                    req.metadata,
                    req.generation_settings,
                    req.__publish_time__ as request_time,
                    comp.__publish_time__ as complete_time,
                    comp.image_url
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
                raise DBError("More than one image found with the same id")

            return self.map_row_to_image(rows[0])
        except Exception as e:
            self.logger.error(f"Error while fetching image by id: {e}")
            raise DBError(
                f"An error occurred while fetching image with id {id}") from e
