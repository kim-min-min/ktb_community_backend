# app/controllers/post_controller.py
from fastapi import HTTPException, UploadFile
from datetime import datetime
import os
import uuid
from app.models import post_model


# 게시글 이미지 업로드 폴더
POST_UPLOAD_DIR = "post_uploads"
os.makedirs(POST_UPLOAD_DIR, exist_ok=True)



# -----------------------------
# 게시글 목록 조회
# -----------------------------
def list_posts_controller() -> dict:
    posts_sorted = post_model.list_posts_desc()
    return {
        "success": True,
        "posts": posts_sorted
    }



# -----------------------------
# 게시글 추가
# -----------------------------
async def create_post_controller(
    title: str,
    content: str,
    image_file: UploadFile | None
) -> dict:

    global POST_ID_SEQ

    title = (title or "").strip()
    content = (content or "").strip()

    # 1) 제목 검증 (최대 26자)
    if not title:
        raise HTTPException(status_code=400, detail="제목을 입력해주세요.")

    if len(title) > 26:
        raise HTTPException(status_code=400, detail="제목은 최대 26자까지 작성 가능합니다.")

    # 2) 내용 검증
    if not content:
        raise HTTPException(status_code=400, detail="내용을 입력해주세요.")

    # 3) 이미지 처리
    image_path = None
    if image_file is not None and image_file.filename:
        ext = image_file.filename.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{ext}"
        image_path = os.path.join(POST_UPLOAD_DIR, file_name)

        # 파일 저장
        with open(image_path, "wb") as f:
            f.write(await image_file.read())

    # 4) 게시글 데이터 생성 (Model 계층에 위임)
    new_post = post_model.create_post(
        title=title,
        content=content,
        image_path=image_path,
    )

    return {
        "success": True,
        "message": "게시글이 등록되었습니다.",
        "post": new_post,
    }


# -----------------------------
# 게시글 상세 조회
# -----------------------------
def get_post_detail_controller(post_id: int) -> dict:
    post = post_model.increase_views(post_id)

    # 상세 페이지 들어올 때마다 조회수 +1
    post["views"] += 1

    result = {
        **post,
        "comment_count": len(post["comments"]),
    }

    return {
        "success": True,
        "post": result,
    }


# -----------------------------
# 좋아요 토글
# -----------------------------
def toggle_like_controller(post_id: int, liked_now: bool) -> dict:
    post = post_model.toggle_like(post_id, liked_now)

    return {
        "success": True,
        "likes": post["likes"],
        "liked": not liked_now if liked_now in (True, False) else True,
    }



# -----------------------------
# 댓글 등록
# -----------------------------
def add_comment_controller(post_id: int, content: str, writer: str | None = None) -> dict:
    content = (content or "").strip()

    if not content:
        raise HTTPException(status_code=400, detail="댓글 내용을 입력해주세요.")

    data = post_model.add_comment(post_id, content, writer)
    post = data["post"]
    comment = data["comment"]

    return {
        "success": True,
        "comment": comment,
        "comment_count": len(post["comments"]),
    }



# -----------------------------
# 댓글 수정
# -----------------------------
def update_comment_controller(post_id: int, comment_id: int, content: str) -> dict:
    content = (content or "").strip()
    if not content:
        raise HTTPException(status_code=400, detail="댓글 내용을 입력해주세요.")

    comment = post_model.update_comment(post_id, comment_id, content)

    return {
        "success": True,
        "comment": comment,
    }



# -----------------------------
# 댓글 삭제
# -----------------------------
def delete_comment_controller(post_id: int, comment_id: int) -> dict:
    after = post_model.delete_comment(post_id, comment_id)

    return {
        "success": True,
        "comment_count": after,
    }



# -----------------------------
# 게시글 수정
# -----------------------------
async def update_post_controller(
    post_id: int,
    title: str,
    content: str,
    image_file: UploadFile | None,
) -> dict:

    title = (title or "").strip()
    content = (content or "").strip()

    # 1) 제목 검증 (최대 26자)
    if not title:
        raise HTTPException(status_code=400, detail="제목을 입력해주세요.")
    if len(title) > 26:
        raise HTTPException(status_code=400, detail="제목은 최대 26자까지 작성 가능합니다.")

    # 2) 내용 검증
    if not content:
        raise HTTPException(status_code=400, detail="내용을 입력해주세요.")

    # 3) 이미지 처리 (새 이미지가 오면 저장)
    new_image_path = None
    if image_file is not None and image_file.filename:
        ext = image_file.filename.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{ext}"
        new_image_path = os.path.join(POST_UPLOAD_DIR, file_name)

        with open(new_image_path, "wb") as f:
            f.write(await image_file.read())


    # 4) Model 계층을 통해 게시글 내용 수정
    post = post_model.update_post(
        post_id=post_id,
        title=title,
        content=content,
        new_image_path=new_image_path,
    )

    return {
        "success": True,
        "message": "게시글이 수정되었습니다.",
        "post": post,
    }
