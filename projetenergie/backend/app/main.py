from fastapi import FastAPI
from app.api.api_v1.api import api_router
from app.core.config import settings
from app.initial_data import main as init_data
from app.middleware import add_cors_middleware

def create_app() -> FastAPI:
    app = FastAPI(
        title="Smart Senelec API",
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    @app.on_event("startup")
    def startup_event():
        init_data()

    add_cors_middleware(app)

    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app

app = create_app()

@app.get("/")
def root():
    return {"message": "Welcome to Smart Senelec API"}
