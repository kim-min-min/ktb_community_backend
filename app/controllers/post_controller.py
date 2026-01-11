# app/controllers/post_controller.py
from fastapi import HTTPException, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session
import os, uuid
import requests
from app.models.post_model import Comment




from app.crud.post_crud import (
    create_post,
    delete_post, 
    get_post_or_404,
    increase_views,
    toggle_like,
    update_post,
    add_comment,
    update_comment,
    delete_comment,
    list_posts_cursor
)
from app.models.user_model import User   # 추가

POST_UPLOAD_DIR = "post_uploads"
os.makedirs(POST_UPLOAD_DIR, exist_ok=True)
AGENT_BASE_URL = os.getenv("AGENT_BASE_URL", "").rstrip("/")

# -----------------------------
# 게시글 목록 조회
# -----------------------------
def list_posts_controller(
    db: Session,
    last_id: int | None,
    size: int,
) -> dict:
    posts = list_posts_cursor(db, last_id, size)

    result: list[dict] = []
    for p in posts:
        result.append(
            {
                "id": p.id,
                "title": p.title,
                "content": p.content,
                "image_path": p.image_path,
                "likes": p.likes,
                "views": p.views,
                "created_at": p.created_at,
                "user_id": p.user_id,
                "user_nickname": p.user.nickname if p.user else None,  
            }
        )

    next_last_id = posts[-1].id if posts else None

    return {
        "success": True,
        "posts": result,                   # ORM 말고 순수 dict 리스트
        "last_id": next_last_id,
        "has_more": next_last_id is not None,
    }



# -----------------------------
# 게시글 추가 (로그인 유저 사용)
# -----------------------------
async def create_post_controller(
    db: Session,
    title: str,
    content: str,
    image_file: UploadFile | None,
    user: User,                       # 현재 로그인 유저
    background_tasks: BackgroundTasks | None,
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

    # user.id 를 함께 넘겨서 user_id 컬럼에 저장하도록
    post = create_post(db, title, content, image_path, user_id=user.id)
    if background_tasks:
        background_tasks.add_task(trigger_moderation, "post", post.id, post.content)
    
    return {"success": True, "message": "게시글이 등록되었습니다.", "post": post}


# -----------------------------
# 게시글 상세 조회 (+ 조회수 증가)
# -----------------------------
def get_post_detail_controller(db: Session, post_id: int) -> dict:
    post = increase_views(db, post_id)

    # 댓글을 created_at 기준으로 정렬:
    comments = (
        db.query(Comment)
        .filter(
            Comment.post_id == post.id,
            Comment.moderation_status != "HIDDEN",
        )
        .order_by(Comment.created_at.asc())
        .all()
    )

    comment_list: list[dict] = []
    for c in comments:
        comment_list.append(
            {
                "id": c.id,
                "post_id": c.post_id,
                "content": c.content,
                "writer": c.writer,        # 화면에 보여줄 닉네임
                "user_id": c.user_id,      # 작성자 FK
                "created_at": c.created_at,
            }
        )

    post_dict = {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "image_path": post.image_path,
        "likes": post.likes,
        "views": post.views,
        "created_at": post.created_at,
        "user_id": post.user_id,
        "user_nickname": post.user.nickname if post.user else None,
        "comments": comment_list,     
    }

    return {
        "success": True,
        "post": post_dict,
    }


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
    user: User,
    background_tasks: BackgroundTasks | None,
) -> dict:
    if not content.strip():
        raise HTTPException(400, "댓글 내용을 입력해주세요.")

    data = add_comment(
        db=db,
        post_id=post_id,
        content=content,
        user_id=user.id,
        writer=user.nickname,
    )

    comment = data["comment"]

    if background_tasks:
        background_tasks.add_task(
            trigger_moderation,
            "comment",          # target_type
            comment.id,         # target_id
            comment.content,    # content
        )

    return {"success": True, "comment": comment}



# -----------------------------
# 댓글 수정 (작성자만)
# -----------------------------
def update_comment_controller(
    db: Session,
    post_id: int,
    comment_id: int,
    content: str,
    user: User,
    background_tasks: BackgroundTasks | None,
) -> dict:
    if not content.strip():
        raise HTTPException(400, "댓글 내용을 입력해주세요.")

    comment = update_comment(
        db=db,
        post_id=post_id,
        comment_id=comment_id,
        content=content,
        user_id=user.id,    # 본인 댓글인지 crud쪽에서 확인 가능하게
    )
    if background_tasks:
        background_tasks.add_task(
            trigger_moderation,
            "comment",
            comment.id,
            comment.content,
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
    user: User,         
    background_tasks: BackgroundTasks | None,
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
        new_image_path=new_image_path,
        user_id=user.id,      # 작성자 검증용
    )
    
    if background_tasks:
        background_tasks.add_task(
            trigger_moderation,
            "post",
            post.id,
            post.content,
        )

    return {"success": True, "message": "게시글이 수정되었습니다.", "post": post}




# -----------------------------
# agent 트리거
# -----------------------------
def trigger_moderation(target_type: str, target_id: int, content: str):
    if not AGENT_BASE_URL:
        return
    try:
        requests.post(
            f"{AGENT_BASE_URL}/moderate",
            json={
                "target_type": target_type,
                "target_id": target_id,
                "content": content,
            },
            headers={"X-Internal-Call": "true"},
            timeout=3,
        )
    except Exception:
        pass




        
