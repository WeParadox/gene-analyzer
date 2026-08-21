from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import logging
import time

from .models.database import init_db, async_session, Gene, Sequence, Alignment
from .routers import genes, sequences, alignment
from .config import settings
from sqlalchemy import select

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A web tool for analyzing amplified gene sequences with pairwise alignment (BLASTN scoring)",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time, 4))
    return response


app.include_router(genes.router)
app.include_router(sequences.router)
app.include_router(alignment.router)


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Gene sequence analysis tool with BLASTN pairwise alignment",
        "docs": "/docs",
        "redoc": "/redoc",
        "api": "/api"
    }


@app.get("/health")
async def health():
    async with async_session() as db:
        gene_count = await db.scalar(select(Gene.id).limit(1).with_only_columns(Gene.id).count() if hasattr(Gene.id, 'count') else select(Gene))
        try:
            gene_count_result = await db.execute(select(Gene))
            gene_count = len(gene_count_result.scalars().all())
            sequence_count_result = await db.execute(select(Sequence))
            sequence_count = len(sequence_count_result.scalars().all())
            alignment_count_result = await db.execute(select(Alignment))
            alignment_count = len(alignment_count_result.scalars().all())
            db_status = "healthy"
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            gene_count = 0
            sequence_count = 0
            alignment_count = 0
            db_status = "unhealthy"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "version": settings.APP_VERSION,
        "database": db_status,
        "gene_count": gene_count,
        "sequence_count": sequence_count,
        "alignment_count": alignment_count,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred",
            "code": "INTERNAL_ERROR"
        }
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not found",
            "detail": f"The requested resource was not found",
            "code": "NOT_FOUND"
        }
    )


@app.exception_handler(422)
async def validation_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "detail": str(exc),
            "code": "VALIDATION_ERROR"
        }
    )
