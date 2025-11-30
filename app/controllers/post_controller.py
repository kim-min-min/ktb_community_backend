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

POST_UPLOAD_DIR = "post_uploads"
os.makedirs(POST_UPLOAD_DIR, exist_ok=True)


# -----------------------------
# 게시글 목록 조회
# -----------------------------
def list_posts_controller(db: Session) -> dict:
    posts = list_posts_desc(db)
    return {"success": True, "posts": posts}


# -----------------------------
# 게시글 추가
# -----------------------------
async def create_post_controller(
    db: Session,
    title: str,
    content: str,
    image_file: UploadFile | None
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

    post = create_post(db, title, content, image_path)

    return {"success": True, "message": "게시글이 등록되었습니다.", "post": post}


# -----------------------------
# 게시글 상세 조회 (+ 조회수 증가)
# -----------------------------
def get_post_detail_controller(db: Session, post_id: int) -> dict:
    post = increase_views(db, post_id)
    return {"success": True, "post": post}




# -----------------------------
# 게시글 삭제
# -----------------------------
def delete_post_controller(db: Session, post_id: int) -> dict:
    post = delete_post(db, post_id)

    # 이미지 파일 같이 지우기 (있으면)
    if post.image_path and os.path.exists(post.image_path):
        try:
            os.remove(post.image_path)
        except OSError:
            pass

    return {
        "success": True,
        "message": "게시글이 삭제되었습니다.",
        "post_id": post_id,
    }


# -----------------------------
# 좋아요 토글
# -----------------------------
def toggle_like_controller(db: Session, post_id: int, liked_now: bool) -> dict:
    post = toggle_like(db, post_id, liked_now)
    return {"success": True, "likes": post.likes, "liked": not liked_now}


# -----------------------------
# 댓글 등록
# -----------------------------
def add_comment_controller(db: Session, post_id: int, content: str, writer: str | None) -> dict:
    if not content.strip():
        raise HTTPException(400, "댓글 내용을 입력해주세요.")

    data = add_comment(db, post_id, content, writer)
    return {"success": True, "comment": data["comment"]}


# -----------------------------
# 댓글 수정
# -----------------------------
def update_comment_controller(db: Session, post_id: int, comment_id: int, content: str) -> dict:
    if not content.strip():
        raise HTTPException(400, "댓글 내용을 입력해주세요.")

    comment = update_comment(db, post_id, comment_id, content)
    return {"success": True, "comment": comment}


# -----------------------------
# 댓글 삭제
# -----------------------------
def delete_comment_controller(db: Session, post_id: int, comment_id: int) -> dict:
    remaining = delete_comment(db, post_id, comment_id)
    return {"success": True, "remaining_comments": remaining}


# -----------------------------
# 게시글 수정
# -----------------------------
async def update_post_controller(
    db: Session,
    post_id: int,
    title: str,
    content: str,
    image_file: UploadFile | None
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

    post = update_post(db, post_id, title, content, new_image_path)

    return {"success": True, "message": "게시글이 수정되었습니다.", "post": post}
