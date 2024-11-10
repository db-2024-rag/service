from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    host: str = '0.0.0.0'
    port: int = 8080
    generation_k: int = 5
    pg_host: str = 'localhost'
    pg_username: str = 'postgres'
    pg_password: SecretStr = 'postgres'
    pg_db: str = 'postgres'
    llm_host: str = 'http://localhost:8000/v1'
    llm_key: str = 'test'
    llm_model: str = 'Vikhrmodels/Vikhr-Llama3.1-8B-Instruct-R-21-09-24'
    ocr_gpu: bool = False
    total_top: int = 15
    web_top_files: int = 3

    @property
    def pg_dsn(self) -> str:
        return f'postgresql+asyncpg://{self.pg_username}:{self.pg_password.get_secret_value()}@{self.pg_host}/{self.pg_db}'

    model_config = SettingsConfigDict(env_nested_delimiter='__')
