import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(name)s - %(message)s")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import async_session, engine
from app.models import Base
from app.routers import (
    audit,
    documents,
    dossiers,
    entities,
    fiscal,
    health,
    reconciliation,
    risk,
)
from app.services.fiscal_service import set_loaded_lists
from app.utils.csv_parser import load_all_lists

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    asyncio.create_task(_load_fiscal_lists())  # Descarga 9 CSVs del SAT al iniciar.
    validity_task = asyncio.create_task(
        _periodic_validity_check()
    )  # Vigencias cada hora.

    yield

    validity_task.cancel()


# SCHEDULER DE VIGENCIAS: cada hora revisa todos los dossiers activos.
# Si un doc vencio, CSF no es del mes, o fiscal > 3 meses -> needs_update automatico.
async def _run_validity_cycle():
    from app.models.dossier import Dossier, DossierStatus
    from app.services.dossier_service import check_and_update_validity
    from sqlalchemy import select

    async with async_session() as db:
        result = await db.execute(
            select(Dossier.id).where(
                Dossier.status.notin_([DossierStatus.DRAFT.value, DossierStatus.REJECTED.value])
            )
        )
        dossier_ids = result.scalars().all()
        updated = 0
        for did in dossier_ids:
            new_status = await check_and_update_validity(db, did)
            if new_status == DossierStatus.NEEDS_UPDATE.value:
                updated += 1
        await db.commit()
        if updated:
            logger.info("Validity check: %d dossiers marked as needs_update", updated)


async def _periodic_validity_check():
    await asyncio.sleep(60)
    while True:
        try:
            await _run_validity_cycle()
        except Exception as e:
            logger.error("Validity check failed: %s", e)
        await asyncio.sleep(3600)


# CARGA INICIAL: descarga 9 CSVs publicos del SAT en memoria (~500K+ RFCs).
async def _load_fiscal_lists():
    try:
        logger.info("Loading SAT fiscal lists...")
        lists = await load_all_lists()
        set_loaded_lists(lists)
        total_rfcs = sum(len(v) for v in lists.values())
        logger.info(
            "SAT fiscal lists loaded: %d lists, %d total RFCs", len(lists), total_rfcs
        )
    except Exception as e:
        logger.error("Failed to load fiscal lists: %s", e)


app = FastAPI(title="KYB Platform", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080",
        "https://kyb-platform.fly.dev",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(entities.router, prefix="/api/v1")
app.include_router(dossiers.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(fiscal.router, prefix="/api/v1")
app.include_router(reconciliation.router, prefix="/api/v1")
app.include_router(risk.router, prefix="/api/v1")
app.include_router(audit.router, prefix="/api/v1")


STATIC_DIR = Path(__file__).parent / "static"

if STATIC_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api/"):
            from fastapi import HTTPException

            raise HTTPException(status_code=404, detail="Not found")
        file_path = (STATIC_DIR / full_path).resolve()
        if not str(file_path).startswith(str(STATIC_DIR.resolve())):
            from fastapi import HTTPException

            raise HTTPException(status_code=404)
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(STATIC_DIR / "index.html")
else:

    @app.get("/")
    def root():
        return {"message": "KYB Platform API"}
