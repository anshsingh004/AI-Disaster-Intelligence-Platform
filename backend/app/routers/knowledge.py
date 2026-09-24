import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.knowledge import KnowledgeBase
from app.models.user import User
from app.schemas.knowledge import KnowledgeBaseCreate, KnowledgeBaseRecord
from app.dependencies import get_current_user, RequireRole
from app.core.response import success_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/knowledge", tags=["Operational Knowledge Base"])


@router.get("", response_model=dict)
def list_knowledge_docs(
    category: Optional[str] = Query(None, description="Filter by category (e.g. SOP, EVACUATION, HAZMAT)"),
    search: Optional[str] = Query(None, description="Wildcard keyword search in title or content"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List operational SOPs, field protocols, and knowledge base documents for RAG context."""
    query = db.query(KnowledgeBase)

    if category:
        query = query.filter(KnowledgeBase.category.ilike(f"%{category}%"))
    if search:
        query = query.filter(
            KnowledgeBase.title.ilike(f"%{search}%") | KnowledgeBase.content.ilike(f"%{search}%")
        )

    total = query.count()
    offset = (page - 1) * limit
    docs = query.order_by(KnowledgeBase.created_at.desc()).offset(offset).limit(limit).all()
    pages = (total + limit - 1) // limit

    records = [KnowledgeBaseRecord.model_validate(doc).model_dump(mode="json") for doc in docs]
    return success_response(data={
        "items": records,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages
    })


@router.get("/{doc_id}", response_model=dict)
def get_knowledge_doc(
    doc_id: int,
    db: Session = Depends(get_db)
):
    """Retrieve a specific operational knowledge document by ID."""
    doc = db.query(KnowledgeBase).filter(KnowledgeBase.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge base record not found")

    record = KnowledgeBaseRecord.model_validate(doc).model_dump(mode="json")
    return success_response(data=record)


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_knowledge_doc(
    payload: KnowledgeBaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole(["EOC_LEAD", "ADMINISTRATOR", "OPERATOR"]))
):
    """Add a new SOP, protocol, or incident guideline to the knowledge base."""
    new_doc = KnowledgeBase(
        title=payload.title,
        category=payload.category,
        content=payload.content,
        source_url=payload.source_url
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    record = KnowledgeBaseRecord.model_validate(new_doc).model_dump(mode="json")
    return success_response(data=record)


@router.delete("/{doc_id}", response_model=dict)
def delete_knowledge_doc(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole(["EOC_LEAD", "ADMINISTRATOR"]))
):
    """Delete a knowledge base document. Requires EOC_LEAD or ADMINISTRATOR role."""
    doc = db.query(KnowledgeBase).filter(KnowledgeBase.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge base record not found")

    db.delete(doc)
    db.commit()
    return success_response(data={"id": doc_id, "deleted": True})
