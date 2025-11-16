# app/models/user_model.py

from __future__ import annotations
from typing import Optional

# 실제 "DB" 대신 사용할 메모리 저장소
TEMP_USERS: list[dict] = []


def create_user(email: str, password: str, nickname: str,
                profile_image_path: str | None) -> dict:
    """회원 생성 후 TEMP_USERS 에 추가"""
    user = {
        "email": email,
        "password": password,
        "nickname": nickname,
        "profile_image_path": profile_image_path,
    }
    TEMP_USERS.append(user)
    return user


def get_user_by_email(email: str) -> Optional[dict]:
    """이메일로 유저 한 명 조회"""
    for u in TEMP_USERS:
        if u["email"] == email:
            return u
    return None


def is_nickname_duplicated(nickname: str, exclude_email: str | None = None) -> bool:
    """닉네임 중복 여부 (본인 제외 옵션)"""
    for u in TEMP_USERS:
        if u["nickname"] == nickname and u["email"] != exclude_email:
            return True
    return False


def delete_user_by_email(email: str) -> Optional[dict]:
    """이메일로 유저 삭제하고, 삭제된 유저를 반환"""
    user = get_user_by_email(email)
    if user:
        TEMP_USERS.remove(user)
    return user


def update_user_password(email: str, new_password: str) -> Optional[dict]:
    """유저 비밀번호 변경"""
    user = get_user_by_email(email)
    if user:
        user["password"] = new_password
    return user
