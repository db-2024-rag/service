import pickle
from collections import defaultdict
from dataclasses import dataclass
from uuid import UUID

import torch

from cprag.settings import AppSettings
from cprag.storage.db import DbClient
from cprag.storage.orm import StoredFilePart, StoredFileOrm

import sqlalchemy as sa

from cprag.vectorizer.e5 import Vectorizer


@dataclass
class SearchItem:
    file_name: str
    file_id: str
    page: int
    text: str


class SearchIndex:
    def __init__(self, settings: AppSettings, db: DbClient, vectorizer: Vectorizer):
        self._settings = settings
        self._db = db
        self._vectorizer = vectorizer
        self._search_items = None
        self._doc_vec = None

    async def build(self):
        async with self._db.session() as sess:
            items = await sess.execute(
                sa.select(
                    StoredFilePart, StoredFileOrm.file_name, StoredFileOrm.id
                ).join(
                    StoredFileOrm,
                    StoredFileOrm.id == StoredFilePart.file_id
                )
            )
            items = items.fetchall()

        search_items = []

        vectors = []
        for storage_part, file_name, file_id in items:
            item = SearchItem(
                file_name=file_name,
                file_id=file_id,
                page=storage_part.page,
                text=storage_part.text_enrich
            )
            search_items.append(item)
            vectors.append(pickle.loads(storage_part.vector))

        doc_vec = torch.stack(vectors, dim=0)

        self._search_items = search_items
        self._doc_vec = doc_vec

    async def lookup(self, query: str) -> dict[UUID, list[SearchItem]]:
        query_vec = self._vectorizer.vectorize_query(query)
        similarities = self._doc_vec @ query_vec
        top_k = similarities.argsort(descending=True)[:self._settings.total_top]
        items = [self._search_items[i] for i in top_k]
        answer_by_file = defaultdict(list)
        seen_files = set()
        for item in items:
            if len(seen_files) >= self._settings.web_top_files and item.file_id not in seen_files:
                continue
            seen_files.add(item.file_id)
            answer_by_file[item.file_id].append(item)
        return answer_by_file
