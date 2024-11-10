import os
import sys
from asyncio import new_event_loop
from pathlib import Path

import pandas as pd
from tqdm import tqdm

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
    settings.web_top_files = 1
    settings.total_top = 10

    db = DbClient(settings.pg_dsn)
    llm = LLM(settings)
    vectorizer = Vectorizer(settings)
    index = SearchIndex(settings, db, vectorizer)
    answernator = Answernator(index, llm)

    await db.connect()
    await index.build()

    df = pd.read_csv(sys.argv[1])
    new_entries = []
    for row in tqdm(df.itertuples()):
        answer = await answernator.answer(row.question)
        new_entries.append({
            'question': row.question,
            'filename': answer[0].file_name.split('.')[0],
            'slide_number': answer[0].slides[0] if len(answer[0].slides) > 0 else 0,
            'answer': answer[0].answer
        })
    pd.DataFrame(new_entries).to_csv('outputs.csv', index=None)


if __name__ == '__main__':
    new_event_loop().run_until_complete(main())
