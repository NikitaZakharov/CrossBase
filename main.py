import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.router import api_router
from core.config import settings
from core.redis import cache


app = FastAPI(title='CrossBase', openapi_url='/api/openapi.json')

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix='/api')


@app.on_event('startup')
async def startup_event():
    await cache.init()


@app.on_event('shutdown')
async def shutdown_event():
    await cache.close()


if __name__ == "__main__" and settings.DEBUG:
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
