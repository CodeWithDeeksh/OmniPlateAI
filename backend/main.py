from fastapi import FastAPI

from backend.api.cameras import router as cameras_router
from backend.api.deferred import router as deferred_router
from backend.api.detections import router as detections_router
from backend.api.errors import (
	ApiError,
	api_error_handler,
	validation_error_handler,
)
from fastapi.exceptions import RequestValidationError
from backend.api.health import router as health_router
from backend.api.vehicles import router as vehicles_router


def create_app() -> FastAPI:
	app = FastAPI(title="SIH26127 Backend", version="0.1.0")
	app.add_exception_handler(ApiError, api_error_handler)
	app.add_exception_handler(RequestValidationError, validation_error_handler)
	app.include_router(health_router, prefix="/api")
	app.include_router(cameras_router, prefix="/api")
	app.include_router(detections_router, prefix="/api")
	app.include_router(vehicles_router, prefix="/api")
	app.include_router(deferred_router, prefix="/api")
	return app


app = create_app()
