import re
import time

import easyocr
import magic
from PIL import Image
from pdf2image import convert_from_bytes
from tqdm import tqdm

from cprag.settings import AppSettings


class OcrReader:
    def __init__(self, settings: AppSettings):
        self.reader = easyocr.Reader(['ru', 'en'], gpu=settings.ocr_gpu, model_storage_directory='ocrmodel')

    def recognize_text(self, image: Image.Image) -> list[str]:
        temp_filename = f"temp_{int(time.time())}.jpg"
        image.convert("RGB").save(temp_filename)
        paragraphs = self.reader.readtext(temp_filename, paragraph=False, detail=0)
        return [x for x in paragraphs if re.match('[a-zA-Z0-9а-яА-ЯёЁ]', x)]

    def __call__(self, file_contents: bytes) -> dict[int, str]:
        mime = magic.from_buffer(file_contents, mime=True)
        match mime:
            case 'application/pdf':
                paragraphs = {}
                pages = convert_from_bytes(file_contents)
                for page_num, page_image in enumerate(tqdm(pages)):
                    paragraphs[page_num + 1] = '\n'.join(self.recognize_text(page_image))
                return paragraphs
            case 'text/plain':
                return {1: file_contents.decode('utf-8')}
            case _:
                raise ValueError('Unsupported file format')

