from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.rest import router as rest_router
from app.api.rpc import router as rpc_router
from app.config import get_settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title="Выборщик лотов", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(rest_router)
app.include_router(rpc_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
