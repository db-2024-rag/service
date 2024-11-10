import pickle
import uuid

import magic

from cprag.llm.llm import LLM
from cprag.recognize.ocr import OcrReader
from cprag.storage.db import DbClient

import sqlalchemy as sa

from cprag.storage.orm import StoredFileOrm, StoredFilePart
from cprag.vectorizer.e5 import Vectorizer


class FileProcessor:
    def __init__(self, db: DbClient, ocr: OcrReader, llm: LLM, vectorizer: Vectorizer):
        self._db = db
        self._ocr = ocr
        self._llm = llm
        self._vectorizer = vectorizer

    async def new_file(self, name: str, contents: bytes):
        mime = magic.from_buffer(contents, mime=True)

        file_id = uuid.uuid4()
        async with self._db.session() as sess, sess.begin():
            await sess.execute(sa.insert(StoredFileOrm).values(
                id=file_id,
                file_name=name,
                mime=mime,
                contents=contents
            ))

        paragraph = self._ocr(contents)
        page_to_id = {}
        async with self._db.session() as sess, sess.begin():
            for page_num, contents in paragraph.items():
                page_id = uuid.uuid4()
                page_to_id[page_num] = page_id
                await sess.execute(sa.insert(StoredFilePart).values(
                    id=page_id,
                    file_id=file_id,
                    page=page_num,
                    text=contents
                ))

        all_contents = '\n\n'.join([f'Слайд {page_num}: {contents}' for page_num, contents in paragraph.items()])[:8000]

        topic = self._llm.run([
            {'role': 'system', 'content': 'Тебе на вход будет дана презентация в разбивке по слайдам. Напиши название продукта, о котором говорится в презентации (если это презентация продукта), либо напиши тему презентации (если это общая презентация). Обычно нужная информация дана на 1 слайде.'},
            {'role': 'user', 'content': all_contents}
        ])[:1000]

        async with self._db.session() as sess, sess.begin():
            await sess.execute(sa.update(StoredFileOrm).values(topic=topic).where(StoredFileOrm.id == file_id))

        async with self._db.session() as sess, sess.begin():
            for page_num, contents in paragraph.items():
                page_id = page_to_id[page_num]
                enrich = f'{topic}\n\n\n{contents}'
                vector = self._vectorizer.vectorize_document(enrich)
                await sess.execute(sa.update(StoredFilePart).values(vector=pickle.dumps(vector), text_enrich=f'{topic}\n\n\n{contents}').where(StoredFilePart.id == page_id))


    async def download(self, idx: uuid.UUID) -> tuple[bytes, str]:
        async with self._db.session() as sess:
            result = await sess.scalar(sa.select(StoredFileOrm).where(
                StoredFileOrm.id == idx
            ))
            return result.contents, result.mime
