from fastapi import APIRouter, File, UploadFile, Body, Query
from typing import Literal
from pydantic import BaseModel
from app.services import fitz_service, markdown_service

router = APIRouter(prefix="/markdown", tags=["Markdown"])

class URLRequest(BaseModel):
    url: str

@router.post("/upload-pdf")
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

@router.post("/upload-file-by-url")
async def upload_file_by_url(payload: URLRequest):
    file_path, filename = markdown_service.download_file_from_url(payload.url)
    teks = markdown_service.extract_text_from_pdf(file_path)
    return {"filename": filename, "text": teks}

@router.post("/upload-file-by-url2")
async def upload_file_by_url2(url: str = Body(...)):
    markdown = markdown_service.convert_to_markdown_from_url(url)
    return {"filename": url.split("/")[-1], "markdown": markdown}

@router.post("/upload-file-docling")
async def upload_file_docling(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        markdown = markdown_service.convert_to_markdown_from_file(contents, file.filename)
        return {"filename": file.filename, "markdown": markdown}
    except Exception as e:
        return {"error": str(e)}
