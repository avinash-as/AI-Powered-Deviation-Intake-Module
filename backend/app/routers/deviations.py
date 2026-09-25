from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Deviation
from ..schemas import DeviationCreate, DeviationOut

router = APIRouter(prefix="/api/deviations", tags=["deviations"])


def _next_id(db: Session) -> str:
    from datetime import datetime

    year = datetime.utcnow().year
    count = db.query(Deviation).count() + 1
    return f"DEV-{year}-{count:04d}"


@router.get("", response_model=list[DeviationOut])
def list_deviations(db: Session = Depends(get_db)):
    return db.query(Deviation).order_by(desc(Deviation.id)).limit(100).all()


@router.post("", response_model=DeviationOut, status_code=201)
def create_deviation(payload: DeviationCreate, db: Session = Depends(get_db)):
    if not payload.title.strip():
        raise HTTPException(400, "Title is required (use AI panel to extract it).")
    row = Deviation(**payload.model_dump(), deviation_id=_next_id(db))
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/{deviation_id}", response_model=DeviationOut)
def get_deviation(deviation_id: str, db: Session = Depends(get_db)):
    row = db.query(Deviation).filter(Deviation.deviation_id == deviation_id).first()
    if not row:
        raise HTTPException(404, "Deviation not found")
    return row
