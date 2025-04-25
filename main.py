from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import markdown_router

app = FastAPI()


app.title = "Docling API"
app.summary = "Created By Hamba Allah"
app.description = "Ini adalah Docling App untuk generate markdown dari dokumen pdf"
app.version = "1.0.0"
app.include_router(markdown_router.router)

app.mount("/static", StaticFiles(directory="uploads"), name="static")