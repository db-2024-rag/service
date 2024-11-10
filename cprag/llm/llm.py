from openai import OpenAI

from cprag.settings import AppSettings


class LLM:
    def __init__(self, settings: AppSettings):
        self._client = OpenAI(
            base_url=settings.llm_host,
            api_key=settings.llm_key,
        )
        self._model = settings.llm_model

    def run(self, messages: dict) -> str:
        completion = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0.0
        )

        return completion.choices[0].message.content
