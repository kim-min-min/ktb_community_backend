# app/routes/post_router.py
from fastapi import APIRouter, Form, File, UploadFile, Body, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.controllers.post_controller import (
    list_posts_controller,
    get_post_detail_controller,
    create_post_controller,
    delete_post_controller,
    toggle_like_controller,
    add_comment_controller,
    update_comment_controller,
    delete_comment_controller,
    update_post_controller,
)

router = APIRouter(prefix="/posts", tags=["posts"])


# -----------------------------
# 게시글 목록 조회
# -----------------------------
@router.get("")
def list_posts(db: Session = Depends(get_db)):
    return list_posts_controller(db)


# -----------------------------
# 게시글 상세 조회
# -----------------------------
@router.get("/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    return get_post_detail_controller(db, post_id)


# -----------------------------
# 게시글 작성
# -----------------------------
@router.post("")
async def create_post(
    title: str = Form(...),
    content: str = Form(...),
    image_file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    return await create_post_controller(db, title, content, image_file)


# -----------------------------
# 게시글 삭제
# -----------------------------
@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
):
    return delete_post_controller(db, post_id)


# -----------------------------
# 좋아요 토글
# -----------------------------
@router.post("/{post_id}/like")
def toggle_like(
    post_id: int,
    liked: bool = Body(..., embed=True),
    db: Session = Depends(get_db),
):
    return toggle_like_controller(db, post_id, liked)


# -----------------------------
# 댓글 등록
# -----------------------------
@router.post("/{post_id}/comments")
def add_comment(
    post_id: int,
    content: str = Form(...),
    writer: str = Form("더미 작성자 1"),
    db: Session = Depends(get_db),
):
    return add_comment_controller(db, post_id, content, writer)


# -----------------------------
# 댓글 수정
# -----------------------------
@router.put("/{post_id}/comments/{comment_id}")
def update_comment(
    post_id: int,
    comment_id: int,
    content: str = Form(...),
    db: Session = Depends(get_db),
):
    return update_comment_controller(db, post_id, comment_id, content)


# -----------------------------
# 댓글 삭제
# -----------------------------
@router.delete("/{post_id}/comments/{comment_id}")
def delete_comment(
    post_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
):
    return delete_comment_controller(db, post_id, comment_id)


# -----------------------------
# 게시글 수정
# -----------------------------
@router.put("/{post_id}")
async def update_post(
    post_id: int,
    title: str = Form(...),
    content: str = Form(...),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    return await update_post_controller(db, post_id, title, content, image)
