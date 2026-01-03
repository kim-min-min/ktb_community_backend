# app/routes/post_router.py
from fastapi import APIRouter, Form, File, UploadFile, Body, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.models.user_model import User

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
# 게시글 목록 조회 (커서 기반)
# -----------------------------
@router.get("")
def list_posts(
    last_id: int | None = Query(None, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_posts_controller(db=db, last_id=last_id, size=size)


# -----------------------------
# 게시글 상세 조회
# -----------------------------
@router.get("/{post_id}")
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  
):
    return get_post_detail_controller(db, post_id)



# -----------------------------
# 게시글 작성
# -----------------------------
@router.post("")
async def create_post(
    background_tasks: BackgroundTasks,          
    title: str = Form(...),
    content: str = Form(...),
    image_file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await create_post_controller(
        db=db,
        title=title,
        content=content,
        image_file=image_file,
        user=current_user,
        background_tasks=background_tasks,      
    )


# -----------------------------
# 게시글 삭제
# -----------------------------
@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),   
):
    return delete_post_controller(
        db=db,
        post_id=post_id,
        user=current_user,                          
    )


# -----------------------------
# 게시글 수정
# -----------------------------
@router.put("/{post_id}")
async def update_post(
    post_id: int,
    title: str = Form(...),
    content: str = Form(...),
    image_file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),   
):
    return await update_post_controller(
        db=db,
        post_id=post_id,
        title=title,
        content=content,
        image_file=image_file,
        user=current_user,                           
    )
    

# -----------------------------
# 좋아요 토글
# -----------------------------
@router.post("/{post_id}/like")
def toggle_like(
    post_id: int,
    liked: bool = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),   
):
    return toggle_like_controller(db, post_id, liked)



# -----------------------------
# 댓글 등록 (로그인 필요)
# -----------------------------
@router.post("/{post_id}/comments")
def add_comment(
    post_id: int,
    content: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),   
):
    return add_comment_controller(
        db=db,
        post_id=post_id,
        content=content,
        user=current_user,                           
    )



# -----------------------------
# 댓글 수정 (로그인 필요)
# -----------------------------
@router.put("/{post_id}/comments/{comment_id}")
def update_comment(
    post_id: int,
    comment_id: int,
    content: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),   
):
    return update_comment_controller(
        db=db,
        post_id=post_id,
        comment_id=comment_id,
        content=content,
        user=current_user,                             
    )



# -----------------------------
# 댓글 삭제 (로그인 필요)
# -----------------------------
@router.delete("/{post_id}/comments/{comment_id}")
def delete_comment(
    post_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  
):
    return delete_comment_controller(
        db=db,
        post_id=post_id,
        comment_id=comment_id,
        user=current_user,                            
    )





