from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import MenuItem, Round
from app.schemas.common import APIResponse
from app.schemas.round import MenuItemOut

router = APIRouter(prefix="/menu", tags=["menu"])


@router.get("", response_model=APIResponse[list[MenuItemOut]])
def list_menu(
    round_id: int = Query(..., description="Round to list menu items for"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    round_ = db.get(Round, round_id)
    if round_ is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบรอบนี้")

    items = db.query(MenuItem).filter(MenuItem.round_id == round_id).order_by(MenuItem.id).all()
    return APIResponse(data=[MenuItemOut.model_validate(i) for i in items], message="ok")
