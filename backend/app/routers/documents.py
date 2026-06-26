import logging
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models.dossier import Dossier
from app.schemas.document import (
    DocumentListResponse,
    DocumentResponse,
    MissingDocumentsResponse,
)
from app.services import document_service
from app.services.classification_service import classify_document
from app.services.extraction_service import extract_document_data
from app.services.storage_service import download_file, get_presigned_url

logger = logging.getLogger(__name__)

router = APIRouter(tags=["documents"])


MAX_FILE_SIZE = 10 * 1024 * 1024


async def _validate_upload(dossier_id: uuid.UUID, document_type: str, file: UploadFile, db: AsyncSession):
    from app.models.document import DocumentType

    dossier = await db.get(Dossier, dossier_id)
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier not found")

    valid_types = {e.value for e in DocumentType}
    if document_type not in valid_types:
        raise HTTPException(
            status_code=400, detail=f"Tipo de documento invalido: {document_type}"
        )

    file_data = await file.read()
    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, detail="Archivo demasiado grande (max 10 MB)"
        )

    return file_data


async def _run_extraction(db: AsyncSession, doc, file_data: bytes):
    try:
        await extract_document_data(db, doc, file_data)
        await db.commit()
        await db.refresh(doc)
    except Exception as e:
        logger.error("Extraction failed for document %s: %s", doc.id, e)
        doc.extraction_status = "failed"
        await db.commit()
        await db.refresh(doc)


@router.post(
    "/dossiers/{dossier_id}/documents", response_model=DocumentResponse, status_code=201
)
async def upload_document(
    dossier_id: uuid.UUID,
    file: UploadFile = File(...),
    document_type: str = Form(...),
    fecha_emision: str | None = Form(None),
    fecha_vencimiento: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
):
    file_data = await _validate_upload(dossier_id, document_type, file, db)

    try:
        doc = await document_service.upload_document(
            db,
            dossier_id=dossier_id,
            document_type=document_type,
            file_name=file.filename or "document",
            file_data=file_data,
            content_type=file.content_type or "application/octet-stream",
            fecha_emision=fecha_emision,
            fecha_vencimiento=fecha_vencimiento,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    await db.commit()
    await db.refresh(doc)
    await _run_extraction(db, doc, file_data)
    return doc


@router.get(
    "/dossiers/{dossier_id}/documents", response_model=list[DocumentListResponse]
)
async def list_documents(
    dossier_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await document_service.list_documents(db, dossier_id)


@router.get(
    "/dossiers/{dossier_id}/documents/checklist",
    response_model=MissingDocumentsResponse,
)
async def document_checklist(
    dossier_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    docs = await document_service.list_documents(db, dossier_id)
    missing = document_service.get_missing_documents(docs)
    return MissingDocumentsResponse(
        missing=missing,
        total_required=5,
        total_present=5 - len(missing),
    )


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    doc = await document_service.get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("/documents/{document_id}/download")
async def download_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    doc = await document_service.get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if not doc.file_key:
        raise HTTPException(
            status_code=404, detail="No file associated with this document"
        )

    url = await get_presigned_url(doc.file_key)
    if not url:
        raise HTTPException(status_code=503, detail="Storage service unavailable")
    return {"download_url": url}


@router.post("/documents/{document_id}/extract", response_model=DocumentResponse)
async def re_extract_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    doc = await document_service.get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if not doc.file_key:
        raise HTTPException(status_code=400, detail="No file to extract from")

    file_data = await download_file(doc.file_key)
    if not file_data:
        raise HTTPException(
            status_code=503, detail="Storage unavailable for re-extraction"
        )

    try:
        await extract_document_data(db, doc, file_data)
        await db.commit()
        await db.refresh(doc)
    except Exception as e:
        logger.error("Re-extraction failed for document %s: %s", doc.id, e)
        doc.extraction_status = "failed"
        await db.commit()
        await db.refresh(doc)
    return doc


@router.delete("/documents/{document_id}", status_code=204)
async def delete_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    deleted = await document_service.delete_document(db, document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    await db.commit()


@router.post("/documents/classify")
async def classify_uploaded_document(
    file: UploadFile = File(...),
):
    file_data = await file.read()
    mime = file.content_type or "application/pdf"
    result = await classify_document(file_data, mime)
    if not result:
        raise HTTPException(
            status_code=503, detail="Classification service unavailable"
        )
    return result
