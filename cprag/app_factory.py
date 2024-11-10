import os
from contextlib import asynccontextmanager
from re import search
from uuid import UUID

from fastapi import FastAPI, UploadFile
from starlette.requests import Request
from starlette.responses import HTMLResponse, Response
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from cprag.answernator.answer import Answernator
from cprag.file_processor.processor import FileProcessor
from cprag.llm.llm import LLM
from cprag.recognize.ocr import OcrReader
from cprag.schema import ChatRequest
from cprag.search.index import SearchIndex
from cprag.settings import AppSettings
from cprag.storage.db import DbClient
from cprag.vectorizer.e5 import Vectorizer


def create_app(settings: AppSettings | None = None) -> FastAPI:
    if not settings:
        settings = AppSettings()

    db = DbClient(settings.pg_dsn)
    ocr = OcrReader(settings)
    llm = LLM(settings)
    vectorizer = Vectorizer(settings)
    file_processor = FileProcessor(db, ocr, llm, vectorizer)
    search_index = SearchIndex(settings, db, vectorizer)
    answernator = Answernator(search_index, llm)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await db.connect()
        await search_index.build()
        yield
        await db.close()

    app = FastAPI(title='CP RAG', lifespan=lifespan)
    app.mount("/static", StaticFiles(directory="static"), name="static")

    templates = Jinja2Templates(directory="templates")

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        return templates.TemplateResponse(
            request=request, name="index.jinja2"
        )

    @app.post('/upload')
    async def upload(file: UploadFile):
        await file_processor.new_file(file.filename, await file.read())
        await search_index.build()
        return 'File uploaded successfully.'

    @app.get('/download/{idx}/{name}')
    async def download(idx: str, name: str):
        content, mime = await file_processor.download(UUID(idx))
        return Response(content=content, media_type=mime)

    @app.post('/chat')
    async def chat(body: ChatRequest):
        answers = await answernator.answer(body.message)
        responses = []
        for answer in answers:
            responses.append({
                'text': f'Слайды {answer.slides}: {answer.answer}',
                'files': [{'id': answer.file_id, 'name': answer.file_name}]
            })

        return {'responses': responses}

    return app