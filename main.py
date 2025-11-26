import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from image import wait_image, image_raw2cv
from metashape import proccess_metashape
from ai import process_image
from fly import fly_start
from grabber import grab_images
app = FastAPI()
logger = logging.getLogger(__name__)

id = 0

@app.middleware("http")
async def error_handler(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.exception("Unhandled error")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )


@app.get("/start_scan")
async def start_scan() -> FileResponse:
    fly_start()
    grab_images()
    proccess_metashape()
    return FileResponse(f"tmp{id}/metashape/image.png", media_type="image/jpeg")


@app.get("/start_upload")
async def start_upload() -> FileResponse:
    proccess_metashape()
    return FileResponse(f"tmp{id}/metashape/image.png", media_type="image/jpeg")

@app.get("/detect")
async def detect() -> FileResponse:
    process_image(f"tmp{id}/metashape")
    return FileResponse(f"tmp{id}/ai/image.png", media_type="image/jpeg")