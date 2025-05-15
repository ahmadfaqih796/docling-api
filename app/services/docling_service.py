import uuid
from io import BytesIO
import re
from typing import List, Tuple

from docling.datamodel.base_models import InputFormat, DocumentStream
from docling.datamodel.pipeline_options import PdfPipelineOptions, EasyOcrOptions
from docling.document_converter import PdfFormatOption, DocumentConverter
from docling_core.types.doc import ImageRefMode, TableItem, PictureItem

from app.services.upload_service import upload_image


class DoclingService:
    def __init__(self):
        self.pipeline_options = self._default_pipeline_options()

    def _default_pipeline_options(self) -> PdfPipelineOptions:
        options = PdfPipelineOptions()
        options.generate_page_images = False
        options.generate_picture_images = True
        options.ocr_options = EasyOcrOptions(lang=["en", "id"])
        return options

    def _extract_images_and_markdown(self, conv_res) -> Tuple[str, List[str]]:
        images_urls = []
        content_md = conv_res.document.export_to_markdown(image_mode=ImageRefMode.PLACEHOLDER)

        for element, _ in conv_res.document.iterate_items():
            if isinstance(element, (TableItem, PictureItem)) and element.image:
                buffer = BytesIO()
                element.image.pil_image.save(buffer, format="PNG")
                buffer.seek(0)

               #  filename = f"{element.id}.png"
                filename = f"{uuid.uuid4()}.png"
                url = upload_image(buffer, filename)

                images_urls.append(url)
                content_md = content_md.replace("<!-- image -->", f"![image]({url})", 1)

        return content_md, images_urls

    def convert(self, filename: str, file_bytes: bytes) -> dict:
        doc_converter = DocumentConverter(
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=self.pipeline_options)}
        )

        conv_res = doc_converter.convert(
            DocumentStream(name=filename, stream=BytesIO(file_bytes)),
            raises_on_error=False,
        )

        if conv_res.errors:
            raise Exception(f"Conversion failed: {conv_res.errors[0].error_message}")

        markdown, images = self._extract_images_and_markdown(conv_res)
        
        markdown = markdown.replace("\\n", "\n")
        markdown = re.sub(r'[ \t]+', ' ', markdown)
        markdown = re.sub(r'\n{2,}', '\n\n', markdown)

        markdown = markdown.strip()

        return {
            "filename": filename,
            "markdown": markdown,
            "images": images
        }
        
    def convert_by_url(self, url: str) -> dict:
        converter = DocumentConverter(
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=self.pipeline_options)}
        )
        conv_res = converter.convert(url)
        if conv_res.errors:
            raise Exception(f"Conversion failed: {conv_res.errors[0].error_message}")

        markdown, images = self._extract_images_and_markdown(conv_res)
        
        markdown = markdown.replace("\\n", "\n")
        markdown = re.sub(r'[ \t]+', ' ', markdown)
        markdown = re.sub(r'\n{2,}', '\n\n', markdown)

        markdown = markdown.strip()

        return {
            "filename": url.split("/")[-1],
            "markdown": markdown,
            "images": images
        }
        
        
