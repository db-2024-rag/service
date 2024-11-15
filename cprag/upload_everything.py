import os
import sys
from asyncio import new_event_loop
from pathlib import Path

from cprag.answernator.answer import Answernator
from cprag.file_processor.processor import FileProcessor
from cprag.llm.llm import LLM
from cprag.recognize.ocr import OcrReader
from cprag.search.index import SearchIndex
from cprag.settings import AppSettings
from cprag.storage.db import DbClient
from cprag.storage.orm import StoredFileOrm
from cprag.vectorizer.e5 import Vectorizer


import sqlalchemy as sa


async def main():
    settings = AppSettings()

    db = DbClient(settings.pg_dsn)
    ocr = OcrReader(settings)
    llm = LLM(settings)
    vectorizer = Vectorizer(settings)
    file_processor = FileProcessor(db, ocr, llm, vectorizer)

    for file in Path(sys.argv[1]).iterdir():
        async with db.session() as sess:
            exists = await sess.scalar(sa.select(StoredFileOrm.id).where(StoredFileOrm.file_name == file.name))
            if not exists:
                print(f'Adding {file.name}')
                await file_processor.new_file(file.name, file.read_bytes())


if __name__ == '__main__':
    new_event_loop().run_until_complete(main())
