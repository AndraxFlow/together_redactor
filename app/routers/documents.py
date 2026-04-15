from fastapi import APIRouter, Depends, status

from app.dependencies import get_current_user
from app.schemas.document import DocumentCreate, DocumentResponse, DocumentUpdate
from app.services.document_service import (
    create_document,
    delete_document,
    get_document_by_id,
    get_documents,
    update_document,
)
from app.services.access_service import get_user_role
from app.models.documents import document_access
from app.db.session import engine


router = APIRouter(tags=["documents"])


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document_endpoint(
    payload: DocumentCreate,
    current_user: dict = Depends(get_current_user),
) -> DocumentResponse:
    doc = create_document(current_user, payload.model_dump())
    return DocumentResponse(**doc)


@router.get("/", response_model=list[DocumentResponse])
def list_documents_endpoint(current_user: dict = Depends(get_current_user)) -> list[DocumentResponse]:
    docs = get_documents(current_user)
    return [DocumentResponse(**doc) for doc in docs]


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document_endpoint(
    document_id: int,
    current_user: dict = Depends(get_current_user),
) -> DocumentResponse:
    doc = get_document_by_id(current_user, document_id)
    return DocumentResponse(**doc)


@router.patch("/{document_id}", response_model=DocumentResponse)
def update_document_endpoint(
    document_id: int,
    payload: DocumentUpdate,
    current_user: dict = Depends(get_current_user),
) -> DocumentResponse:
    doc = update_document(current_user, document_id, payload.model_dump(exclude_unset=True))
    return DocumentResponse(**doc)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document_endpoint(
    document_id: int,
    current_user: dict = Depends(get_current_user),
) -> None:
    delete_document(current_user, document_id)

@router.post("/{document_id}/share")
def share_document(document_id: int, user_id: int, role: str):
    with engine.begin() as conn:
        conn.execute(
            document_access.insert().values(
                document_id=document_id,
                user_id=user_id,
                role=role,
            )
        )

    return {"status": "shared", "role": role}