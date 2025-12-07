# app/controllers/post_controller.py
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
import os, uuid

from app.crud.post_crud import (
    list_posts_desc,
    create_post,
    delete_post, 
    get_post_or_404,
    increase_views,
    toggle_like,
    update_post,
    add_comment,
    update_comment,
    delete_comment,
)
from app.models.user_model import User   # 추가

POST_UPLOAD_DIR = "post_uploads"
os.makedirs(POST_UPLOAD_DIR, exist_ok=True)


# -----------------------------
# 게시글 목록 조회
# -----------------------------
def list_posts_controller(db: Session) -> dict:
    posts = list_posts_desc(db)
    return {"success": True, "posts": posts}


# -----------------------------
# 게시글 추가 (로그인 유저 사용)
# -----------------------------
async def create_post_controller(
    db: Session,
    title: str,
    content: str,
    image_file: UploadFile | None,
    user: User,                       # 현재 로그인 유저
) -> dict:

    title = title.strip()
    content = content.strip()

    if not title:
        raise HTTPException(status_code=400, detail="제목을 입력해주세요.")
    if len(title) > 26:
        raise HTTPException(status_code=400, detail="제목은 최대 26자까지 작성 가능합니다.")
    if not content:
        raise HTTPException(status_code=400, detail="내용을 입력해주세요.")

    # 이미지 처리
    image_path = None
    if image_file and image_file.filename:
        allowed_ext = {"jpg", "jpeg", "png", "gif", "webp"}
        ext = image_file.filename.rsplit(".", 1)[-1].lower()
        if ext not in allowed_ext:
            raise HTTPException(400, "허용되지 않은 이미지 형식입니다.")

        allowed_mime = {"image/jpeg", "image/png", "image/gif", "image/webp"}
        if image_file.content_type not in allowed_mime:
            raise HTTPException(400, "이미지 MIME 타입 오류")

        file_name = f"{uuid.uuid4()}.{ext}"
        image_path = os.path.join(POST_UPLOAD_DIR, file_name)
        with open(image_path, "wb") as f:
            f.write(await image_file.read())

    # ✅ user.id 를 함께 넘겨서 user_id 컬럼에 저장하도록
    post = create_post(db, title, content, image_path, user_id=user.id)

    return {"success": True, "message": "게시글이 등록되었습니다.", "post": post}


# -----------------------------
# 게시글 상세 조회 (+ 조회수 증가)
# -----------------------------
def get_post_detail_controller(db: Session, post_id: int) -> dict:
    post = increase_views(db, post_id)
    return {"success": True, "post": post}


# -----------------------------
# 게시글 삭제 (작성자만 가능)
# -----------------------------
def delete_post_controller(db: Session, post_id: int, user: User) -> dict:
    # 우선 게시글을 가져와서 작성자인지 확인
    post = get_post_or_404(db, post_id)

    if post.user_id != user.id:
        raise HTTPException(status_code=403, detail="본인이 작성한 게시글만 삭제할 수 있습니다.")

    # 실제 삭제
    deleted_post = delete_post(db, post_id)

    # 이미지 파일 같이 지우기 (있으면)
    if deleted_post.image_path and os.path.exists(deleted_post.image_path):
        try:
            os.remove(deleted_post.image_path)
        except OSError:
            pass

    return {
        "success": True,
        "message": "게시글이 삭제되었습니다.",
        "post_id": post_id,
    }


# -----------------------------
# 좋아요 토글 (로그인 여부는 선택)
# -----------------------------
def toggle_like_controller(db: Session, post_id: int, liked_now: bool) -> dict:
    post = toggle_like(db, post_id, liked_now)
    return {"success": True, "likes": post.likes, "liked": not liked_now}


# -----------------------------
# 댓글 등록 (로그인 유저만)
# -----------------------------
def add_comment_controller(
    db: Session,
    post_id: int,
    content: str,
    user: User,          # 로그인 유저
) -> dict:
    if not content.strip():
        raise HTTPException(400, "댓글 내용을 입력해주세요.")

    # writer는 화면용 닉네임, user_id는 FK
    data = add_comment(
        db=db,
        post_id=post_id,
        content=content,
        user_id=user.id,             # FK
        writer=user.nickname,        # 화면 표시용
    )

    return {"success": True, "comment": data["comment"]}


# -----------------------------
# 댓글 수정 (작성자만)
# -----------------------------
def update_comment_controller(
    db: Session,
    post_id: int,
    comment_id: int,
    content: str,
    user: User,          # 로그인 유저
) -> dict:
    if not content.strip():
        raise HTTPException(400, "댓글 내용을 입력해주세요.")

    # 컨트롤러에서 직접 권한 체크할 수도 있고,
    # crud에서 user_id를 받아서 체크하도록 할 수도 있음.
    comment = update_comment(
        db=db,
        post_id=post_id,
        comment_id=comment_id,
        content=content,
        user_id=user.id,    # 본인 댓글인지 crud쪽에서 확인 가능하게
    )
    return {"success": True, "comment": comment}


# -----------------------------
# 댓글 삭제 (작성자만)
# -----------------------------
def delete_comment_controller(
    db: Session,
    post_id: int,
    comment_id: int,
    user: User,          # 로그인 유저
) -> dict:
    remaining = delete_comment(
        db=db,
        post_id=post_id,
        comment_id=comment_id,
        user_id=user.id,       # 본인 댓글인지 crud에서 체크하도록
    )
    return {"success": True, "remaining_comments": remaining}


# -----------------------------
# 게시글 수정 (작성자만)
# -----------------------------
async def update_post_controller(
    db: Session,
    post_id: int,
    title: str,
    content: str,
    image_file: UploadFile | None,
    user: User,          # 로그인 유저
) -> dict:

    title = title.strip()
    content = content.strip()

    if not title:
        raise HTTPException(400, "제목을 입력해주세요.")
    if len(title) > 26:
        raise HTTPException(400, "제목은 최대 26자까지 작성 가능합니다.")
    if not content:
        raise HTTPException(400, "내용을 입력해주세요.")

    new_image_path = None
    if image_file and image_file.filename:
        allowed_ext = {"jpg", "jpeg", "png", "gif", "webp"}
        ext = image_file.filename.rsplit(".", 1)[-1].lower()
        if ext not in allowed_ext:
            raise HTTPException(400, "허용되지 않은 이미지입니다.")

        allowed_mime = {"image/jpeg", "image/png", "image/gif", "image/webp"}
        if image_file.content_type not in allowed_mime:
            raise HTTPException(400, "이미지 MIME 오류")

        file_name = f"{uuid.uuid4()}.{ext}"
        new_image_path = os.path.join(POST_UPLOAD_DIR, file_name)
        with open(new_image_path, "wb") as f:
            f.write(await image_file.read())

    # 수정 시에도 작성자인지 체크하도록 user_id 함께 전달
    post = update_post(
        db=db,
        post_id=post_id,
        title=title,
        content=content,
        image_path=new_image_path,
        user_id=user.id,      # 작성자 검증용
    )

    return {"success": True, "message": "게시글이 수정되었습니다.", "post": post}
