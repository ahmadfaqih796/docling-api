import os
import fitz
import requests
import tempfile
import base64
from docling.document_converter import DocumentConverter

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_upload_file(file, filename="dummy.pdf"):
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(file)
    return file_path
 
def extract_images_from_pdf(file_path: str):
    doc = fitz.open(file_path) 
    images = []

    for page_index in range(len(doc)):
        page = doc[page_index]
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            encoded = base64.b64encode(image_bytes).decode("utf-8")

            images.append({
                "page": page_index + 1,
                "index": img_index,
                "extension": image_ext,
                "base64": "data:image/" + image_ext + ";base64," + encoded
            })
    doc.close()
    return images


def extract_text_from_pdf(file_path: str):
    doc = fitz.open(file_path)
    teks = "".join([page.get_text() for page in doc])
    doc.close()
    return teks.strip()

def download_file_from_url(url: str):
    filename = url.split("/")[-1]
    file_path = os.path.join(UPLOAD_DIR, filename)
    response = requests.get(url)
    with open(file_path, "wb") as f:
        f.write(response.content)
    return file_path, filename

def convert_to_markdown_from_url(url: str):
    converter = DocumentConverter()
    result = converter.convert(url)
    return result.document.export_to_markdown()

def convert_to_markdown_from_file(contents, filename: str):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(contents)
        tmp_path = tmp.name
    converter = DocumentConverter()
    result = converter.convert(tmp_path)
    return result.document.export_to_markdown()
