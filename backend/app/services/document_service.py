import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentType
from app.services import storage_service
from app.services.audit_service import log_action


# UPLOAD: valida MIME/tamano, sube a S3, guarda metadata en DB, registra audit log.
async def upload_document(
    db: AsyncSession,
    *,
    dossier_id: uuid.UUID,
    document_type: str,
    file_name: str,
    file_data: bytes,
    content_type: str,
    fecha_emision: str | None = None,
    fecha_vencimiento: str | None = None,
) -> Document:
    validation_error = storage_service.validate_file(content_type, len(file_data))
    if validation_error:
        raise ValueError(validation_error)

    file_key = storage_service.generate_file_key(dossier_id, document_type, file_name)
    await storage_service.upload_file(file_key, file_data, content_type)

    from datetime import date

    doc = Document(
        dossier_id=dossier_id,
        document_type=document_type,
        file_name=file_name,
        file_key=file_key,
        file_size=len(file_data),
        mime_type=content_type,
        fecha_emision=date.fromisoformat(fecha_emision) if fecha_emision else None,
        fecha_vencimiento=date.fromisoformat(fecha_vencimiento)
        if fecha_vencimiento
        else None,
    )
    db.add(doc)
    await db.flush()

    await log_action(
        db,
        action="document.uploaded",
        dossier_id=dossier_id,
        details={
            "document_id": str(doc.id),
            "document_type": document_type,
            "file_name": file_name,
            "file_size": len(file_data),
        },
    )

    return doc


async def list_documents(db: AsyncSession, dossier_id: uuid.UUID) -> list[Document]:
    result = await db.execute(
        select(Document)
        .where(Document.dossier_id == dossier_id)
        .order_by(Document.created_at.desc())
    )
    return list(result.scalars().all())


async def get_document(db: AsyncSession, document_id: uuid.UUID) -> Document | None:
    return await db.get(Document, document_id)


async def delete_document(db: AsyncSession, document_id: uuid.UUID) -> bool:
    doc = await db.get(Document, document_id)
    if not doc:
        return False

    if doc.file_key:
        await storage_service.delete_file(doc.file_key)

    dossier_id = doc.dossier_id
    await db.delete(doc)
    await db.flush()

    await log_action(
        db,
        action="document.deleted",
        dossier_id=dossier_id,
        details={"document_id": str(document_id), "document_type": doc.document_type},
    )
    return True


# CHECKLIST: 5 docs obligatorios. Los faltantes suman riesgo en el score.
def get_missing_documents(documents: list[Document]) -> list[str]:
    present_types = {d.document_type for d in documents}
    required = [
        DocumentType.ACTA_CONSTITUTIVA.value,
        DocumentType.IDENTIFICACION_REPRESENTANTE.value,
        DocumentType.COMPROBANTE_DOMICILIO.value,
        DocumentType.CONSTANCIA_SITUACION_FISCAL.value,
        DocumentType.MANIFESTACION_PROTESTA.value,
    ]
    return [t for t in required if t not in present_types]
