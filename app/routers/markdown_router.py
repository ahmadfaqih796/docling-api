from fastapi import APIRouter, File, UploadFile, Body, Query
from typing import Literal
from pydantic import BaseModel
from app.services import fitz_service, markdown_service, upload_service

from app.services.docling_service import DoclingService

router = APIRouter(prefix="/markdown", tags=["Markdown"])
docling_service = DoclingService()

class URLRequest(BaseModel):
    url: str
    
@router.post("/convert-pdf-by-dockling")
async def convert_pdf(file: UploadFile = File(...)):
    file_bytes = await file.read()
    result = docling_service.convert(file.filename, file_bytes)
    return result

@router.post("/convert-pdf-by-fitz")
async def upload_pdf(
    file: UploadFile = File(...),
    view_images: Literal["true", "false"] = Query("false", description="Set 'true' untuk ambil gambar", )
    ):
    file_data = await file.read()
    file_path = markdown_service.save_upload_file(file_data, file.filename)
    teks = markdown_service.extract_text_from_pdf(file_path)
    images = []
    if view_images == "true":
        images = fitz_service.extract_images_from_pdf(file_path)
    return {"filename": file.filename, "text": teks.replace("\n", " "), "images": images}

@router.post("/convert-pdf-by-dockling-url")
async def by_url_pdf(payload: URLRequest = Body(...)):
    res = docling_service.convert_by_url(payload.url)
    return res
