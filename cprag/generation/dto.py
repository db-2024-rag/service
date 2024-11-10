from pydantic import BaseModel


class GenerationOutput(BaseModel):
    text: str
    file_name: str
