from asyncio import new_event_loop

from cprag.answernator.answer import Answernator
from cprag.file_processor.processor import FileProcessor
from cprag.llm.llm import LLM
from cprag.recognize.ocr import OcrReader
from cprag.search.index import SearchIndex
from cprag.settings import AppSettings
from cprag.storage.db import DbClient
from cprag.vectorizer.e5 import Vectorizer


async def main():
    settings = AppSettings()

    db = DbClient(settings.pg_dsn)
    ocr = OcrReader(settings)
    llm = LLM(settings)
    vectorizer = Vectorizer(settings)
    file_processor = FileProcessor(db, ocr, llm, vectorizer)
    search_index = SearchIndex(settings, db, vectorizer)
    answernator = Answernator(search_index, llm)


if __name__ == '__main__':
    new_event_loop().run_until_complete(main())
