from datetime import datetime
from uuid import UUID, uuid4
from fastapi import FastAPI, HTTPException, Query
from typing import List
from handlers import get_all_images, get_image_by_id

from models import Txt2ImgGenerationRequestDTO, Txt2ImgImgDTO, Txt2ImgGenerationRequest
from pulsar_utils import close_pulsar_resources, send_generation_request
from repository import close_trino_connection

app = FastAPI()


@app.on_event("shutdown")
async def shutdown_event():
    close_trino_connection()
    close_pulsar_resources()


@app.get("/health/", name="health_route")
async def health_route():
    return {"status": "ok"}


@app.get("/images/", response_model=List[Txt2ImgImgDTO], name="get_all_images_route")
async def get_all_images_route(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
) -> List[Txt2ImgImgDTO]:
    return get_all_images(limit=limit, offset=offset)


@app.get("/images/{image_id}/", response_model=Txt2ImgImgDTO, name="get_image_by_id_route")
async def get_image_by_id_route(image_id: UUID) -> Txt2ImgImgDTO:
    image = get_image_by_id(image_id)
    if not image:
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
