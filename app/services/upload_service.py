import os
from uuid import uuid4

UPLOAD_FOLDER = "uploads/images"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def upload_image(file_stream, filename: str) -> str:
    filename = f"{uuid4().hex}_{filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    with open(filepath, "wb") as f:
        f.write(file_stream.read())

    return f"/static/images/{filename}"
