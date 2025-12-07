# app/controllers/auth_controller.py
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
import re
import uuid
import os

from app.crud.user_crud import (
    create_user,
    get_user_by_email,
    is_nickname_duplicated,
    delete_user,
    update_user_password,
    update_user_profile,
)
from app.core.security import hash_password, verify_password
from app.models.user_model import User                        

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# -----------------------------
# 로그인 컨트롤러 (User 객체 반환)
# -----------------------------
def login_controller(db: Session, payload: dict) -> User:
    email = (payload.get("email") or "").strip()
    pw = payload.get("password") or ""

    # 1) 이메일 검증
    if not email:
        raise HTTPException(status_code=400, detail="이메일을 입력해주세요.")

    email_regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not re.match(email_regex, email):
        raise HTTPException(
            status_code=400,
            detail="올바른 이메일 주소 형식을 입력해주세요. (예: example@example.com)",
        )

    # 2) 비밀번호 검증
    if not pw:
        raise HTTPException(status_code=400, detail="비밀번호를 입력해주세요.")
    if len(pw) < 8 or len(pw) > 20:
        raise HTTPException(status_code=400, detail="비밀번호는 8~20자입니다.")

    # 3) 사용자 찾기
    user = get_user_by_email(db, email)
    if user is None:
        raise HTTPException(status_code=400, detail="아이디 또는 비밀번호를 확인해주세요.")

    # 4) 비밀번호 검증 (해시)
    if not verify_password(pw, user.password):
        raise HTTPException(status_code=400, detail="아이디 또는 비밀번호를 확인해주세요.")

    # 5) 로그인 성공 → User 반환 (토큰 발급은 라우터에서)
    return user


# -----------------------------
# 회원가입 컨트롤러
# -----------------------------
async def signup_controller(db: Session, payload: dict, profile_image: UploadFile):
    email = payload["email"]
    password = payload["password"]
    password_confirm = payload["password_confirm"]
    nickname = payload["nickname"]

    # 1. 이메일 형식 검증
    email_regex = r"[^@]+@[^@]+\.[^@]+"
    if not re.match(email_regex, email):
        raise HTTPException(status_code=400, detail="올바른 이메일 주소 형식을 입력해주세요.")

    # 2. 비밀번호 규칙 검증
    if len(password) < 8 or len(password) > 20:
        raise HTTPException(status_code=400, detail="비밀번호는 8~20자여야 합니다.")
    if not re.search(r"[A-Z]", password):
        raise HTTPException(status_code=400, detail="비밀번호에 대문자가 최소 1개 포함되어야 합니다.")
    if not re.search(r"[a-z]", password):
        raise HTTPException(status_code=400, detail="비밀번호에 소문자가 최소 1개 포함되어야 합니다.")
    if not re.search(r"[0-9]", password):
        raise HTTPException(status_code=400, detail="비밀번호에 숫자가 최소 1개 포함되어야 합니다.")
    if not re.search(r"[\W_]", password):
        raise HTTPException(status_code=400, detail="비밀번호에 특수문자가 최소 1개 포함되어야 합니다.")

    # 3. 비밀번호 확인
    if password != password_confirm:
        raise HTTPException(status_code=400, detail="비밀번호와 비밀번호 확인이 일치하지 않습니다.")

    # 4. 이메일/닉네임 중복 체크
    if get_user_by_email(db, email):
        raise HTTPException(status_code=400, detail="이미 사용 중인 이메일입니다.")
    if is_nickname_duplicated(db, nickname):
        raise HTTPException(status_code=400, detail="이미 사용 중인 닉네임입니다.")

    # 5. 프로필 이미지 처리
    if profile_image is None or not profile_image.filename:
        raise HTTPException(status_code=400, detail="프로필 이미지를 업로드해주세요.")

    allowed_ext = {"jpg", "jpeg", "png", "gif", "webp"}
    ext = profile_image.filename.rsplit(".", 1)[-1].lower()
    if ext not in allowed_ext:
        raise HTTPException(
            status_code=400,
            detail="허용되지 않은 이미지 형식입니다. (jpg, jpeg, png, gif, webp만 가능)",
        )

    allowed_mime = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if profile_image.content_type not in allowed_mime:
        raise HTTPException(
            status_code=400,
            detail="이미지 파일 형식이 올바르지 않습니다.",
        )

    file_name = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    with open(file_path, "wb") as f:
        f.write(await profile_image.read())

    # 6. 비밀번호 해시 후 DB 저장
    hashed_pw = hash_password(password)

    user = create_user(
        db=db,
        email=email,
        password=hashed_pw,
        nickname=nickname,
        profile_image_path=file_path,
    )

    return {
        "message": "회원가입 성공",
        "email": user.email,
        "nickname": user.nickname,
        "profile_image_path": user.profile_image_path,
    }


# -----------------------------
# 회원정보 수정 (JWT 기반)
# -----------------------------
async def update_profile_controller(
    db: Session,
    user: User,        # 현재 로그인 유저
    payload: dict,
    profile_image: UploadFile | None,
):
    nickname = (payload.get("nickname") or "").strip()

    # 1) 닉네임 검증
    if not nickname:
        raise HTTPException(status_code=400, detail="닉네임을 입력해주세요.")
    if len(nickname) > 10:
        raise HTTPException(status_code=400, detail="닉네임은 최대 10자까지 작성 가능합니다.")

    # 2) 닉네임 중복 (본인 제외, id 기준)
    if is_nickname_duplicated(db, nickname, exclude_user_id=user.id):
        raise HTTPException(status_code=400, detail="중복된 닉네임 입니다.")

    profile_image_path = None

    # 3) 프로필 이미지 처리
    if profile_image is not None and profile_image.filename:
        allowed_ext = {"jpg", "jpeg", "png", "gif", "webp"}
        ext = profile_image.filename.rsplit(".", 1)[-1].lower()
        if ext not in allowed_ext:
            raise HTTPException(
                status_code=400,
                detail="허용되지 않은 이미지 형식입니다. (jpg, jpeg, png, gif, webp만 가능)",
            )

        allowed_mime = {"image/jpeg", "image/png", "image/gif", "image/webp"}
        if profile_image.content_type not in allowed_mime:
            raise HTTPException(
                status_code=400,
                detail="이미지 파일 형식이 올바르지 않습니다.",
            )

        file_name = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join(UPLOAD_DIR, file_name)

        with open(file_path, "wb") as f:
            f.write(await profile_image.read())

        # 기존 이미지 삭제
        old_path = user.profile_image_path
        if old_path and os.path.exists(old_path):
            try:
                os.remove(old_path)
            except OSError:
                pass

        profile_image_path = file_path

    # 4) DB 변경
    user = update_user_profile(db, user, nickname, profile_image_path)

    return user


# -----------------------------
# 회원 탈퇴 (JWT 기반)
# -----------------------------
def delete_account_controller(db: Session, user: User) -> dict:
    # 1) 프로필 이미지 경로 미리 저장
    profile_path = user.profile_image_path

    # 2) 유저 삭제
    deleted = delete_user(db, user)

    # 3) 프로필 이미지 파일 삭제
    if profile_path and os.path.exists(profile_path):
        try:
            os.remove(profile_path)
        except OSError:
            pass

    return {
        "message": "회원 탈퇴가 완료되었습니다.",
        "email": deleted.email,
    }


# -----------------------------
# 비밀번호 수정 (JWT 기반)
# -----------------------------
def update_password_controller(db: Session, user: User, payload: dict) -> dict:
    new_pw = payload.get("new_password") or ""
    new_pw_confirm = payload.get("new_password_confirm") or ""

    # 1) 비밀번호 유효성 검사
    if len(new_pw) < 8 or len(new_pw) > 20:
        raise HTTPException(status_code=400, detail="비밀번호는 8~20자여야 합니다.")
    if not re.search(r"[A-Z]", new_pw):
        raise HTTPException(status_code=400, detail="비밀번호에 대문자가 최소 1개 포함되어야 합니다.")
    if not re.search(r"[a-z]", new_pw):
        raise HTTPException(status_code=400, detail="비밀번호에 소문자가 최소 1개 포함되어야 합니다.")
    if not re.search(r"[0-9]", new_pw):
        raise HTTPException(status_code=400, detail="비밀번호에 숫자가 최소 1개 포함되어야 합니다.")
    if not re.search(r"[\W_]", new_pw):
        raise HTTPException(status_code=400, detail="비밀번호에 특수문자가 최소 1개 포함되어야 합니다.")

    # 2) 비밀번호 확인
    if new_pw != new_pw_confirm:
        raise HTTPException(status_code=400, detail="비밀번호와 비밀번호 확인이 일치하지 않습니다.")

    # 3) 기존 비밀번호와 동일한지 (해시 기준 비교)
    if verify_password(new_pw, user.password):
        raise HTTPException(status_code=400, detail="기존 비밀번호와 동일한 비밀번호는 사용할 수 없습니다.")

    # 4) 새 비밀번호 해시 후 저장
    hashed_pw = hash_password(new_pw)
    update_user_password(db, user, hashed_pw)

    return {
        "message": "비밀번호가 성공적으로 수정되었습니다.",
        "email": user.email,
    }
