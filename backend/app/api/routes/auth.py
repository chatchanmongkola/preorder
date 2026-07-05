from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.security import create_access_token
from app.db.session import get_db
from app.models import User, UserRole
from app.schemas.auth import DevLoginRequest, LineCallbackRequest, LiffLoginRequest, TokenResponse
from app.schemas.common import APIResponse
from app.schemas.user import UserOut
from app.services.line_service import LineAuthError, exchange_code_for_profile, verify_id_token

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/line/callback", response_model=APIResponse[TokenResponse])
async def line_callback(payload: LineCallbackRequest, db: Session = Depends(get_db)):
    try:
        profile = await exchange_code_for_profile(
            code=payload.code,
            redirect_uri=payload.redirect_uri or settings.LINE_REDIRECT_URI,
        )
    except LineAuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    line_user_id = profile.get("sub")
    if not line_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid LINE profile response")

    user = db.query(User).filter(User.line_user_id == line_user_id).one_or_none()
    if user is None:
        user = User(
            line_user_id=line_user_id,
            display_name=profile.get("name", "LINE User"),
            picture_url=profile.get("picture"),
        )
        db.add(user)
    else:
        user.display_name = profile.get("name", user.display_name)
        user.picture_url = profile.get("picture", user.picture_url)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=str(user.id))
    return APIResponse(data=TokenResponse(access_token=token), message="เข้าสู่ระบบสำเร็จ")


@router.post("/liff/login", response_model=APIResponse[TokenResponse])
async def liff_login(payload: LiffLoginRequest, db: Session = Depends(get_db)):
    try:
        profile = await verify_id_token(payload.id_token)
    except LineAuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    line_user_id = profile.get("sub")
    if not line_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid LINE profile response")

    user = db.query(User).filter(User.line_user_id == line_user_id).one_or_none()
    if user is None:
        user = User(
            line_user_id=line_user_id,
            display_name=profile.get("name", "LINE User"),
            picture_url=profile.get("picture"),
        )
        db.add(user)
    else:
        user.display_name = profile.get("name", user.display_name)
        user.picture_url = profile.get("picture", user.picture_url)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=str(user.id))
    return APIResponse(data=TokenResponse(access_token=token), message="เข้าสู่ระบบสำเร็จ")


@router.get("/me", response_model=APIResponse[UserOut])
def read_me(current_user: User = Depends(get_current_user)):
    return APIResponse(data=UserOut.model_validate(current_user), message="ok")


@router.post("/dev-login", response_model=APIResponse[TokenResponse])
def dev_login(payload: DevLoginRequest, db: Session = Depends(get_db)):
    """Dev-only shortcut that bypasses real LINE login. Returns 404 in production."""
    if settings.is_production:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    role = UserRole.ADMIN if payload.as_admin else UserRole.USER
    user = db.query(User).filter(User.role == role).first()
    if user is None:
        user = User(
            line_user_id=f"dev-{role.value}-line-id",
            display_name=f"Dev {role.value.title()}",
            role=role,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(subject=str(user.id))
    return APIResponse(data=TokenResponse(access_token=token), message="dev login ok")
