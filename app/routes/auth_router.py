# app/routes/auth_route.py
from fastapi import APIRouter, Form, File, UploadFile
from pydantic import BaseModel

from app.controllers.auth_controller import (
    login_controller,
    signup_controller,
    update_profile_controller,
    delete_account_controller,
    update_password_controller,
)

router = APIRouter(prefix="/auth", tags=["auth"])

# ---- BaseModel ----
class LoginRequest(BaseModel):
    email: str
    password: str


# ---- 로그인 API ----
@router.post("/login")
def login(payload: LoginRequest):

    # BaseModel → dict 로 변환해서 controller로 넘김
    data = payload.dict()

    return login_controller(data)


# ---------- 회원가입 API (이미지 업로드 포함) ----------
@router.post("/signup")
async def signup(
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    nickname: str = Form(...),
    profile_image: UploadFile = File(...)
):

    payload = {
        "email": email,
        "password": password,
        "password_confirm": password_confirm,
        "nickname": nickname,
    }

    # dict + UploadFile 을 controller로 넘김
    return await signup_controller(payload, profile_image)


# ---------- 회원정보 수정 API ----------
@router.put("/profile")
async def update_profile(
    email: str = Form(...),                  
    nickname: str = Form(...),
    profile_image: UploadFile | None = File(None),  
):
    payload = {
        "email": email,
        "nickname": nickname,
    }
    return await update_profile_controller(payload, profile_image)


# ---------- 회원 탈퇴 API ----------
@router.delete("/profile")
def delete_profile(
    email: str = Form(...),   # 프론트에서 현재 로그인 중인 유저 이메일을 넘겨줌
):
    return delete_account_controller(email)


# ---------- 비밀번호 수정 API ----------
@router.put("/password")
def update_password(
    email: str = Form(...),
    new_password: str = Form(...),
    new_password_confirm: str = Form(...),
):
    payload = {
        "email": email,
        "new_password": new_password,
        "new_password_confirm": new_password_confirm,
    }
    return update_password_controller(payload)