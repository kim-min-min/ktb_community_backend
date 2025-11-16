# app/controllers/auth_controller.py
from fastapi import HTTPException, UploadFile
import re
import uuid
import os

TEMP_USERS: list[dict] = []

# 업로드 파일 저장 폴더
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# -- 로그인 컨트롤러 --
def login_controller(payload: dict) -> dict:

    email = (payload.get("email") or "").strip()
    pw = payload.get("password") or ""

    # 1) 이메일 검증
    if not email:
        return {
            "success": False,
            "field": "email",
            "message": "*올바른 이메일 주소 형식을 입력해주세요. (예: example@example.com)"
        }

    email_regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not re.match(email_regex, email):
        return {
            "success": False,
            "field": "email",
            "message": "*올바른 이메일 주소 형식을 입력해주세요. (예: example@example.com)"
        }

    # 2) 비밀번호 검증
    if not pw:
        return {
            "success": False,
            "field": "password",
            "message": "*비밀번호를 입력해주세요"
        }

    if len(pw) < 8 or len(pw) > 20:
        return {
            "success": False,
            "field": "password",
            "message": "*비밀번호는 8~20자입니다."
        }

    # 3) TEMP_USERS 에서 사용자 찾기
    user = None
    for u in TEMP_USERS:
        if u["email"] == email:
            user = u
            break

    if user is None:
        return {
            "success": False,
            "field": "global",
            "message": "*아이디 또는 비밀번호를 확인해주세요"
        }

    # 4) 비밀번호 일치 확인
    if user["password"] != pw:
        return {
            "success": False,
            "field": "global",
            "message": "*아이디 또는 비밀번호를 확인해주세요"
        }

    # 5) 로그인 성공
    return {
        "success": True,
        "message": "로그인 성공",
        "redirect": "/post",
        "nickname": user["nickname"],
        "profile_image_path": user.get("profile_image_path")
    }



# -- 회원가입 컨트롤러 --
async def signup_controller(payload: dict, profile_image: UploadFile):
    email = payload["email"]
    password = payload["password"]
    password_confirm = payload["password_confirm"]
    nickname = payload["nickname"]

    # ---------------------------
    # 1. 이메일 형식 검증
    # ---------------------------
    email_regex = r"[^@]+@[^@]+\.[^@]+"
    if not re.match(email_regex, email):
        raise HTTPException(status_code=400, detail="올바른 이메일 주소 형식을 입력해주세요.")

    # ---------------------------
    # 2. 비밀번호 규칙 검증
    # ---------------------------
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

    # ---------------------------
    # 3. 비밀번호 확인
    # ---------------------------
    if password != password_confirm:
        raise HTTPException(status_code=400, detail="비밀번호와 비밀번호 확인이 일치하지 않습니다.")

    # ---------------------------
    # 4. 프로필 이미지 처리
    # ---------------------------
    file_extension = profile_image.filename.split('.')[-1]
    file_name = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    with open(file_path, "wb") as f:
        f.write(await profile_image.read())


    # 5. 회원 정보를 임시 저장소(TEMP_USERS)에 저장
    TEMP_USERS.append({
        "email": email,
        "password": password,  
        "nickname": nickname,
        "profile_image_path": file_path,
    })

    # ---------------------------
    # 6. 회원가입 성공 응답
    # ---------------------------
    return {
        "message": "회원가입 성공",
        "email": email,
        "nickname": nickname,
        "profile_image_path": file_path
    }


# ---------------------------
#  회원정보 수정 컨트롤러
# ---------------------------
async def update_profile_controller(payload: dict, profile_image: UploadFile | None):

    email = (payload.get("email") or "").strip()
    nickname = (payload.get("nickname") or "").strip()

    # 1) 이메일로 유저 찾기
    user = None
    for u in TEMP_USERS:
        if u["email"] == email:
            user = u
            break

    if user is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    # 2) 닉네임 검증
    if not nickname:
        raise HTTPException(status_code=400, detail="닉네임을 입력해주세요.")

    if len(nickname) > 10:
        raise HTTPException(status_code=400, detail="닉네임은 최대 10자까지 작성 가능합니다.")

    # 닉네임 중복 (본인 제외)
    if any(u["nickname"] == nickname and u["email"] != email for u in TEMP_USERS):
        raise HTTPException(status_code=400, detail="중복된 닉네임 입니다.")

    # 3) 프로필 이미지 처리
    if profile_image is not None and profile_image.filename:
        ext = profile_image.filename.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join(UPLOAD_DIR, file_name)

        with open(file_path, "wb") as f:
            f.write(await profile_image.read())


        old_path = user.get("profile_image_path")
        if old_path and os.path.exists(old_path):
            try:
                os.remove(old_path)
            except OSError:
                pass

        user["profile_image_path"] = file_path

    # 4) 닉네임 업데이트
    user["nickname"] = nickname

    return {
        "message": "회원정보가 수정되었습니다.",
        "email": user["email"],
        "nickname": user["nickname"],
        "profile_image_path": user.get("profile_image_path"),
    }

# -----------------------------
# 회원 탈퇴 컨트롤러
# -----------------------------
def delete_account_controller(email: str) -> dict:
    email = (email or "").strip()

    if not email:
        raise HTTPException(status_code=400, detail="이메일이 필요합니다.")

    # 1) 유저 찾기
    target = None
    for u in TEMP_USERS:
        if u["email"] == email:
            target = u
            break

    if target is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    # 2) 프로필 이미지 파일 삭제
    profile_path = target.get("profile_image_path")
    if profile_path and os.path.exists(profile_path):
        try:
            os.remove(profile_path)
        except OSError:
            pass

    # 3) TEMP_USERS 에서 제거
    TEMP_USERS.remove(target)

    return {
        "message": "회원 탈퇴가 완료되었습니다.",
        "email": email,
    }


# -----------------------------
# 비밀번호 수정 컨트롤러
# -----------------------------
def update_password_controller(payload: dict) -> dict:
    email = (payload.get("email") or "").strip()
    new_pw = payload.get("new_password") or ""
    new_pw_confirm = payload.get("new_password_confirm") or ""

    # 1) 사용자 찾기
    user = None
    for u in TEMP_USERS:
        if u["email"] == email:
            user = u
            break

    if user is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    # 2) 비밀번호 유효성 검사
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

    # 3) 비밀번호 확인 일치
    if new_pw != new_pw_confirm:
        raise HTTPException(status_code=400, detail="비밀번호와 비밀번호 확인이 일치하지 않습니다.")

    # 4) 기존 비밀번호와 같으면 오류
    if user["password"] == new_pw:
        raise HTTPException(status_code=400, detail="기존 비밀번호와 동일한 비밀번호는 사용할 수 없습니다.")

    # 5) 비밀번호 업데이트
    user["password"] = new_pw

    return {
        "message": "비밀번호가 성공적으로 수정되었습니다.",
        "email": email,
    }