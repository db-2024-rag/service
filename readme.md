# Запуск
1. Установить в систему `pyenv`, `libmagic`, драйвера nvidia (нужна карта от rtx 3090), `docker-compose`.
2. Установить питон: `pyenv install 3.11.4`
3. Установить окружение: `poetry env use $(pyenv which python)`
4. Установить пакеты: `poetry install`
5. Запустить LLM: `poetry run vllm serve --dtype half --max-model-len 12000 -tp 1 Vikhrmodels/Vikhr-Llama3.1-8B-Instruct-R-21-09-24 --api-key test --gpu-memory-utilization 0.8`
6. Запустить Postgres: `docker compose up`
7. Накатить миграции: `poetry run alembic upgrade head`
8. Запустить сервис: `poetry run python -m cprag`
9. Веб-интерфейс будет доступен на `http://localhost:8080`