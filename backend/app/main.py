from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes.auth import router as auth_router
from app.api.routes.menu import router as menu_router
from app.api.routes.orders import router as orders_router
from app.api.routes.rounds import router as rounds_router
from app.api.routes.telegram import router as telegram_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title="Preorder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Keep the {data, error, message} envelope even for errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"data": None, "error": str(exc.detail), "message": str(exc.detail)},
    )


app.include_router(auth_router)
app.include_router(rounds_router)
app.include_router(menu_router)
app.include_router(orders_router)
app.include_router(telegram_router)


@app.get("/health")
def health() -> dict:
    return {"data": {"status": "ok"}, "error": None, "message": "healthy"}
