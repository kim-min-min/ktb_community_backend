# app/routes/post_router.py
from fastapi import APIRouter, Form, File, UploadFile, Body
from app.controllers.post_controller import (
    list_posts_controller,
    get_post_detail_controller,
    create_post_controller,
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
def list_posts():
    return list_posts_controller()


# -----------------------------
# 게시글 상세 조회
# -----------------------------
@router.get("/{post_id}")
def get_post(post_id: int):
    return get_post_detail_controller(post_id)


# -----------------------------
# 게시글 작성
# -----------------------------
@router.post("")
async def create_post(
    title: str = Form(...),
    content: str = Form(...),
    image_file: UploadFile | None = File(None),  # 이미지 선택 안 할 수도 있으니까 None 허용
):
    return await create_post_controller(title, content, image_file)


# -----------------------------
# 좋아요 토글
# -----------------------------
@router.post("/{post_id}/like")
def toggle_like(
    post_id: int,
    liked: bool = Body(..., embed=True),   # { "liked": true/false }
):
    return toggle_like_controller(post_id, liked)


# -----------------------------
# 댓글 등록
# -----------------------------
@router.post("/{post_id}/comments")
def add_comment(
    post_id: int,
    content: str = Form(...),
    writer: str = Form("더미 작성자 1"),  # 로그인 붙이면 토큰에서 꺼내서 넘기면 됨
):
    return add_comment_controller(post_id, content, writer)


# -----------------------------
# 댓글 수정
# -----------------------------
@router.put("/{post_id}/comments/{comment_id}")
def update_comment(
    post_id: int,
    comment_id: int,
    content: str = Form(...),
):
    return update_comment_controller(post_id, comment_id, content)


# -----------------------------
# 댓글 삭제
# -----------------------------
@router.delete("/{post_id}/comments/{comment_id}")
def delete_comment(
    post_id: int,
    comment_id: int,
):
    return delete_comment_controller(post_id, comment_id)


# -----------------------------
# 게시글 수정
# -----------------------------
@router.put("/{post_id}")
async def update_post(
    post_id: int,
    title: str = Form(...),
    content: str = Form(...),
    image: UploadFile | None = File(None),  
):
    return await update_post_controller(post_id, title, content, image)