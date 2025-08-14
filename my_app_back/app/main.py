from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback
import logging

from app.core.config import settings
from app.api.api_v2.api.router import pose_evaluation_router

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=True,
)


@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logging.error(f"Exception occurred: {str(e)}")
        logging.error(f"Traceback:\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(e), "traceback": traceback.format_exc()},
        )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    logging.error(f"HTTP Exception: {str(exc.detail)}")
    logging.error(f"Traceback:\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": str(exc.detail),
            "status_code": exc.status_code,
            "traceback": traceback.format_exc(),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logging.error(f"Validation error: {str(exc)}")
    logging.error(f"Traceback:\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": str(exc),
            "body": exc.body,
            "errors": exc.errors(),
            "traceback": traceback.format_exc(),
        },
    )


# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(pose_evaluation_router, prefix=settings.API_V2_STR)


@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI backend!"}
