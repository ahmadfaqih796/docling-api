import os
import fitz
import base64
import hashlib

UPLOAD_IMAGE_DIR = "uploads/images"
os.makedirs(UPLOAD_IMAGE_DIR, exist_ok=True)

def get_image_hash(image_bytes: bytes) -> str:
    return hashlib.md5(image_bytes).hexdigest()

def save_image_to_file(image_bytes: bytes, ext: str) -> str:
    image_hash = get_image_hash(image_bytes)
    filename = f"{image_hash}.{ext}"
    path = os.path.join(UPLOAD_IMAGE_DIR, filename)

    if not os.path.exists(path):
        with open(path, "wb") as f:
            f.write(image_bytes)

    return f"/static/images/{filename}"

def extract_images_from_pdf(file_path: str):
    doc = fitz.open(file_path) 
    images = []
    seen_hashes = set()

    for page_index, page in enumerate(doc):
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            ext = base_image["ext"]

            image_hash = get_image_hash(image_bytes)
            if image_hash in seen_hashes:
                continue
            seen_hashes.add(image_hash)

            base64_image = base64.b64encode(image_bytes).decode("utf-8")
            image_url = save_image_to_file(image_bytes, ext)

            images.append({
                "page": page_index + 1,
                "index": img_index,
                "extension": ext,
               #  "base64": f"data:image/{ext};base64,{base64_image}",
                "url": image_url
            })

    doc.close()
    return images
