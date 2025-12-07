from fastapi import APIRouter, Form, File, UploadFile, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel 

from app.database import get_db

from app.controllers.auth_controller import (
    login_controller,
    signup_controller,
    update_profile_controller,
    delete_account_controller,
    update_password_controller,
)

from app.core.security import create_access_token         
from app.dependencies.auth import get_current_user        
from app.models.user_model import User                     

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


# ---- 로그인 API ----
@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    1) 로그인 검증 (login_controller)
    2) 성공 시 JWT access_token 발급
    """
    data = payload.dict()

    user: User = login_controller(db, data)

    # JWT 토큰 발급 (sub에 user.id 사용)
    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "success": True,
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname,
        },
    }


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


# ---- 내 정보 조회 ----
@router.get("/me")
def read_me(current_user: User = Depends(get_current_user)):
    """
    현재 로그인한 사용자 정보 반환
    Authorization: Bearer <token> 필요
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "nickname": current_user.nickname,
        "profile_image": current_user.profile_image_path,
    }


# ---- 회원정보 수정 ----
@router.put("/profile")
async def update_profile(
    nickname: str = Form(...),
    profile_image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  
):
    payload = {"nickname": nickname}
    return await update_profile_controller(
        db=db,
        user=current_user,          
        payload=payload,
        profile_image=profile_image,
    )


# ---- 회원 탈퇴 ----
@router.delete("/profile")
def delete_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user), 
):
    return delete_account_controller(
        db=db,
        user=current_user,         
    )


# ---- 비밀번호 변경 ----
@router.put("/password")
def update_password(
    new_password: str = Form(...),
    new_password_confirm: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  
):
    payload = {
        "new_password": new_password,
        "new_password_confirm": new_password_confirm,
    }
    return update_password_controller(
        db=db,
        user=current_user,        
        payload=payload,
    )
