from fastapi import APIRouter, Form, File, UploadFile, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from pydantic import BaseModel 

from app.controllers.auth_controller import (
    login_controller,
    signup_controller,
    update_profile_controller,
    delete_account_controller,
    update_password_controller,
)

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


# ---- 로그인 API ----
@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    data = payload.dict()
    return login_controller(db, data)


# ---- 회원가입 ----
@router.post("/signup")
async def signup(
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    nickname: str = Form(...),
    profile_image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    payload = {
        "email": email,
        "password": password,
        "password_confirm": password_confirm,
        "nickname": nickname,
    }
    return await signup_controller(db, payload, profile_image)


# ---- 회원정보 수정 ----
@router.put("/profile")
async def update_profile(
    email: str = Form(...),
    nickname: str = Form(...),
    profile_image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    payload = {"email": email, "nickname": nickname}
    return await update_profile_controller(db, payload, profile_image)


# ---- 회원 탈퇴 ----
@router.delete("/profile")
def delete_profile(
    email: str = Form(...),
    db: Session = Depends(get_db),
):
    return delete_account_controller(db, email)


# ---- 비밀번호 변경 ----
@router.put("/password")
def update_password(
    email: str = Form(...),
    new_password: str = Form(...),
    new_password_confirm: str = Form(...),
    db: Session = Depends(get_db),
):
    payload = {
        "email": email,
        "new_password": new_password,
        "new_password_confirm": new_password_confirm,
    }
    return update_password_controller(db, payload)
