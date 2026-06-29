import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies import get_db
from app.models.entity import LegalEntity, LegalRepresentative, Shareholder
from app.schemas.entity import (
    EntityCreate,
    EntityListResponse,
    EntityResponse,
    EntityUpdate,
    LegalRepresentativeCreate,
    LegalRepresentativeResponse,
    ShareholderCreate,
    ShareholderResponse,
)
from app.services.audit_service import log_action
from app.services.fiscal_service import quick_rfc_lookup
from app.utils.rfc_validator import is_valid_rfc

router = APIRouter(prefix="/entities", tags=["entities"])


@router.post("", response_model=EntityResponse, status_code=201)
async def create_entity(payload: EntityCreate, db: AsyncSession = Depends(get_db)):
    normalized_rfc = payload.rfc.upper().strip()
    if not is_valid_rfc(normalized_rfc):
        raise HTTPException(
            status_code=400, detail=f"RFC format invalid: {payload.rfc}"
        )

    existing = await db.execute(
        select(LegalEntity).where(LegalEntity.rfc == normalized_rfc)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409, detail=f"Entity with RFC {payload.rfc} already exists"
        )

    entity = LegalEntity(
        rfc=normalized_rfc,
        razon_social=payload.razon_social.strip(),
        nombre_comercial=payload.nombre_comercial,
        domicilio_fiscal=payload.domicilio_fiscal,
        codigo_postal=payload.codigo_postal,
        regimen_fiscal=payload.regimen_fiscal,
        fecha_constitucion=payload.fecha_constitucion,
        objeto_social=payload.objeto_social,
    )
    db.add(entity)
    await db.flush()

    for rep in payload.representatives:
        db.add(LegalRepresentative(entity_id=entity.id, **rep.model_dump()))
    for sh in payload.shareholders:
        db.add(Shareholder(entity_id=entity.id, **sh.model_dump()))

    await log_action(
        db, action="entity.created", entity_id=entity.id, details={"rfc": entity.rfc}
    )
    await db.commit()

    return await _get_entity_or_404(db, entity.id)


@router.get("", response_model=list[EntityListResponse])
async def list_entities(
    skip: int = 0,
    limit: int = 50,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(LegalEntity)
        .offset(skip)
        .limit(limit)
        .order_by(LegalEntity.created_at.desc())
    )
    if search:
        query = query.where(
            LegalEntity.rfc.icontains(search)
            | LegalEntity.razon_social.icontains(search)
        )
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/check-rfc/{rfc}")
async def check_rfc(
    rfc: str,
    exclude_entity_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    normalized = rfc.upper().strip()
    valid = is_valid_rfc(normalized)
    query = select(LegalEntity).where(LegalEntity.rfc == normalized)
    if exclude_entity_id:
        query = query.where(LegalEntity.id != exclude_entity_id)
    result = await db.execute(query)
    exists = result.scalar_one_or_none() is not None
    sat = quick_rfc_lookup(normalized)
    return {
        "rfc": normalized,
        "valid": valid,
        "exists": exists,
        **sat,
    }


@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(entity_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await _get_entity_or_404(db, entity_id)


@router.put("/{entity_id}", response_model=EntityResponse)
async def update_entity(
    entity_id: uuid.UUID,
    payload: EntityUpdate,
    db: AsyncSession = Depends(get_db),
):
    entity = await _get_entity_or_404(db, entity_id)
    update_data = payload.model_dump(exclude_unset=True)
    if "rfc" in update_data and update_data["rfc"]:
        update_data["rfc"] = update_data["rfc"].upper().strip()
        if not is_valid_rfc(update_data["rfc"]):
            raise HTTPException(
                status_code=400, detail=f"RFC format invalid: {update_data['rfc']}"
            )
        if update_data["rfc"] != entity.rfc:
            existing = await db.execute(
                select(LegalEntity).where(LegalEntity.rfc == update_data["rfc"])
            )
            if existing.scalar_one_or_none():
                raise HTTPException(
                    status_code=409,
                    detail=f"Ya existe una entidad con RFC {update_data['rfc']}",
                )
    if "razon_social" in update_data and update_data["razon_social"]:
        update_data["razon_social"] = update_data["razon_social"].strip()
    for field, value in update_data.items():
        setattr(entity, field, value)

    await log_action(
        db, action="entity.updated", entity_id=entity.id, details=update_data
    )
    await db.commit()
    return await _get_entity_or_404(db, entity_id)


@router.post(
    "/{entity_id}/representatives",
    response_model=LegalRepresentativeResponse,
    status_code=201,
)
async def add_representative(
    entity_id: uuid.UUID,
    payload: LegalRepresentativeCreate,
    db: AsyncSession = Depends(get_db),
):
    await _get_entity_or_404(db, entity_id)
    rep = LegalRepresentative(entity_id=entity_id, **payload.model_dump())
    db.add(rep)
    await log_action(
        db,
        action="representative.added",
        entity_id=entity_id,
        details={"nombre": rep.nombre_completo},
    )
    await db.commit()
    await db.refresh(rep)
    return rep


@router.post(
    "/{entity_id}/shareholders", response_model=ShareholderResponse, status_code=201
)
async def add_shareholder(
    entity_id: uuid.UUID,
    payload: ShareholderCreate,
    db: AsyncSession = Depends(get_db),
):
    await _get_entity_or_404(db, entity_id)
    sh = Shareholder(entity_id=entity_id, **payload.model_dump())
    db.add(sh)
    await log_action(
        db,
        action="shareholder.added",
        entity_id=entity_id,
        details={"nombre": sh.nombre_completo},
    )
    await db.commit()
    await db.refresh(sh)
    return sh


@router.delete("/{entity_id}", status_code=204)
async def delete_entity(
    entity_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    entity = await _get_entity_or_404(db, entity_id)
    await log_action(
        db,
        action="entity.deleted",
        entity_id=entity.id,
        details={"rfc": entity.rfc},
    )
    await db.delete(entity)
    await db.commit()


@router.delete("/{entity_id}/representatives/{rep_id}", status_code=204)
async def delete_representative(
    entity_id: uuid.UUID,
    rep_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    await _get_entity_or_404(db, entity_id)
    rep = await db.get(LegalRepresentative, rep_id)
    if not rep or rep.entity_id != entity_id:
        raise HTTPException(status_code=404, detail="Representative not found")
    await db.delete(rep)
    await log_action(
        db,
        action="representative.deleted",
        entity_id=entity_id,
        details={"nombre": rep.nombre_completo},
    )
    await db.commit()


@router.delete("/{entity_id}/shareholders/{sh_id}", status_code=204)
async def delete_shareholder(
    entity_id: uuid.UUID,
    sh_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    await _get_entity_or_404(db, entity_id)
    sh = await db.get(Shareholder, sh_id)
    if not sh or sh.entity_id != entity_id:
        raise HTTPException(status_code=404, detail="Shareholder not found")
    await db.delete(sh)
    await log_action(
        db,
        action="shareholder.deleted",
        entity_id=entity_id,
        details={"nombre": sh.nombre_completo},
    )
    await db.commit()


async def _get_entity_or_404(db: AsyncSession, entity_id: uuid.UUID) -> LegalEntity:
    result = await db.execute(
        select(LegalEntity)
        .where(LegalEntity.id == entity_id)
        .options(
            selectinload(LegalEntity.representatives),
            selectinload(LegalEntity.shareholders),
        )
    )
    entity = result.scalar_one_or_none()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity
