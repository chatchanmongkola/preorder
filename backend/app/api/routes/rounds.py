from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Round, RoundStatus
from app.schemas.common import APIResponse
from app.schemas.round import RoundOut, RoundSummaryOut
from app.services.round_service import build_round_summary, get_effective_status

router = APIRouter(prefix="/rounds", tags=["rounds"])


def _to_round_out(round_: Round) -> RoundOut:
    return RoundOut(
        id=round_.id,
        name=round_.name,
        opens_at=round_.opens_at,
        closes_at=round_.closes_at,
        status=get_effective_status(round_).value,
    )


def _find_current_round(db: Session) -> Round | None:
    for round_ in db.query(Round).order_by(Round.opens_at.desc()).all():
        if get_effective_status(round_) == RoundStatus.OPEN:
            return round_
    return None


@router.get("/current", response_model=APIResponse[RoundOut])
def get_current_round(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    round_ = _find_current_round(db)
    if round_ is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่มีรอบที่เปิดอยู่ในขณะนี้")
    return APIResponse(data=_to_round_out(round_), message="ok")


@router.get("/{round_id}", response_model=APIResponse[RoundOut])
def get_round(round_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    round_ = db.get(Round, round_id)
    if round_ is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบรอบนี้")
    return APIResponse(data=_to_round_out(round_), message="ok")


@router.get("/{round_id}/summary", response_model=APIResponse[RoundSummaryOut])
def get_round_summary(round_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    round_ = db.get(Round, round_id)
    if round_ is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบรอบนี้")

    summary = build_round_summary(db, round_)
    return APIResponse(data=summary, message="ok")

