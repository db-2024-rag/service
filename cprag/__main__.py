import uvicorn

from cprag.settings import AppSettings

if __name__ == '__main__':
    settings = AppSettings()
    uvicorn.run(
        'cprag.app_factory:create_app',
        factory=True,
        host=settings.host,
        port=settings.port,
        workers=1
    )
