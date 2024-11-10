import json
from dataclasses import dataclass

from cprag.llm.llm import LLM
from cprag.search.index import SearchIndex


GROUNDED_SYSTEM_PROMPT = "Your task is to answer the user's questions using only the information from the provided documents. Give two answers to each question: one with a list of relevant document identifiers and the second with the answer to the question itself, using documents with these identifiers."



@dataclass
class LLMAnswer:
    answer: str
    slides: list[int]
    file_name: str
    file_id: str



class Answernator:
    def __init__(self, index: SearchIndex, llm: LLM):
        self._index = index
        self._llm = llm

    async def answer(self, query: str) -> list[LLMAnswer]:
        found = await self._index.lookup(query)

        answers = []

        for file_id, slides in found.items():
            documents = [
                {
                    "doc_id": slide.page,
                    "title": f"Слайд {slide.page}",
                    "content": slide.text
                }
                for slide in slides
            ]
            sample_history = [
                {'role': 'system', 'content': GROUNDED_SYSTEM_PROMPT},
                {'role': 'documents', 'content': json.dumps(documents, ensure_ascii=False)},
                {'role': 'user', 'content': query}
            ]
            relevant_indexes = self._llm.run(
                messages=sample_history
            )
            relevant_id_num = json.loads(relevant_indexes)['relevant_doc_ids']
            final_answer = self._llm.run(
                messages=sample_history + [{'role': 'assistant', 'content': relevant_indexes}],
            )
            answers.append(LLMAnswer(answer=final_answer, slides=relevant_id_num, file_name=slides[0].file_name, file_id=slides[0].file_id))
        return answers