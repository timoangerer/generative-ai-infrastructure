import logging
from typing import List
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from business_logic import get_all_images, get_image_by_id
from config import get_config
from models import (Txt2ImgGenerationRequest, Txt2ImgGenerationRequestDTO,
                    Txt2ImgImgDTO)
from otel import setup_otel
from pulsar_utils import close_pulsar_resources, send_generation_request
from repository import DBError

config = get_config()
setup_otel()

logger = logging.getLogger(__name__)

app = FastAPI()


@app.on_event("shutdown")
async def shutdown_event():
    close_pulsar_resources()


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error occured: {exc}")
    return JSONResponse(content={"detail": "An unexpected error occurred. Please try again later."}, status_code=500)


@app.exception_handler(DBError)
async def db_error_handler(request: Request, exc: DBError):
    logger.error(f"Database error occurred: {exc}")
    return JSONResponse(content={"detail": "An internal error occurred. Please try again later."}, status_code=500)


@app.get("/health/", name="health_route")
async def health_route():
    return {"status": "ok"}


@app.get("/images/", response_model=List[Txt2ImgImgDTO], name="get_all_images_route")
async def get_all_images_route(
    limit: int = Query(
        20, ge=1, le=100, description="Number of images to retrieve, between 1 and 100"),
    offset: int = Query(
        0, ge=0, description="Offset for pagination, starting from 0")
) -> List[Txt2ImgImgDTO]:
    return get_all_images(limit=limit, offset=offset)


@app.get("/images/{image_id}/", response_model=Txt2ImgImgDTO, name="get_image_by_id_route")
async def get_image_by_id_route(image_id: UUID) -> Txt2ImgImgDTO:
    image = get_image_by_id(image_id)
    if not image:
        logger.error(f"Image with id {image_id} not found")
        raise HTTPException(status_code=404, detail="Image not found")
    return image


@app.post("/images/", response_model=UUID, name="generate_image_route")
async def generate_image_route(req: Txt2ImgGenerationRequestDTO) -> UUID:
    request_id = uuid4()
    generation_request = Txt2ImgGenerationRequest(
        id=request_id,
        metadata=req.metadata,
        generation_settings=req.generation_settings,
    )

    send_generation_request(generation_request)
    return request_id

FastAPIInstrumentor.instrument_app(app)
