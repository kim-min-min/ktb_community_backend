# app/controllers/post_controller.py
from fastapi import HTTPException, UploadFile
from datetime import datetime
import os
import uuid

# 임시 저장용 메모리 DB
TEMP_POSTS: list[dict] = []
POST_ID_SEQ = 1  # 자동 증가 id 용
COMMENT_ID_SEQ = 1       # 댓글 자동 증가 id

# 게시글 이미지 업로드 폴더
POST_UPLOAD_DIR = "post_uploads"
os.makedirs(POST_UPLOAD_DIR, exist_ok=True)

# -----------------------------
# 게시글 찾기
# -----------------------------
def _get_post_or_404(post_id: int) -> dict:
    for post in TEMP_POSTS:
        if post["id"] == post_id:
            return post
    raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")



# -----------------------------
# 게시글 목록 조회
# -----------------------------
def list_posts_controller() -> dict:
    posts_sorted = sorted(TEMP_POSTS, key=lambda x: x["id"], reverse=True)
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

    # 4) 게시글 데이터 생성 (임시 메모리 저장)
    new_post = {
        "id": POST_ID_SEQ,
        "title": title,
        "content": content,
        "image_path": image_path,
        "likes": 0,
        "views": 0,
        "comments": [],  
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    TEMP_POSTS.append(new_post)
    POST_ID_SEQ += 1

    return {
        "success": True,
        "message": "게시글이 등록되었습니다.",
        "post": new_post,
    }


# -----------------------------
# 게시글 상세 조회
# -----------------------------
def get_post_detail_controller(post_id: int) -> dict:
    post = _get_post_or_404(post_id)

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
    post = _get_post_or_404(post_id)

    if not liked_now:
        post["likes"] += 1
        liked_after = True
    else:
        if post["likes"] > 0:
            post["likes"] -= 1
        liked_after = False

    return {
        "success": True,
        "likes": post["likes"],
        "liked": liked_after,
    }


# -----------------------------
# 댓글 등록
# -----------------------------
def add_comment_controller(post_id: int, content: str, writer: str | None = None) -> dict:
    global COMMENT_ID_SEQ

    post = _get_post_or_404(post_id)
    content = (content or "").strip()

    if not content:
        raise HTTPException(status_code=400, detail="댓글 내용을 입력해주세요.")

    comment = {
        "id": COMMENT_ID_SEQ,
        "writer": writer or "더미 작성자 1",
        "content": content,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    post["comments"].append(comment)
    COMMENT_ID_SEQ += 1

    return {
        "success": True,
        "comment": comment,
        "comment_count": len(post["comments"]),
    }


# -----------------------------
# 댓글 수정
# -----------------------------
def update_comment_controller(post_id: int, comment_id: int, content: str) -> dict:
    post = _get_post_or_404(post_id)

    content = (content or "").strip()
    if not content:
        raise HTTPException(status_code=400, detail="댓글 내용을 입력해주세요.")

    for c in post["comments"]:
        if c["id"] == comment_id:
            c["content"] = content
            return {
                "success": True,
                "comment": c,
            }

    raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")


# -----------------------------
# 댓글 삭제
# -----------------------------
def delete_comment_controller(post_id: int, comment_id: int) -> dict:
    post = _get_post_or_404(post_id)

    before = len(post["comments"])
    post["comments"] = [c for c in post["comments"] if c["id"] != comment_id]
    after = len(post["comments"])

    if before == after:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")

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

    post = _get_post_or_404(post_id)

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
    #    - 새 이미지가 오면 저장하고, 기존 경로를 교체
    if image_file is not None and image_file.filename:
        ext = image_file.filename.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{ext}"
        new_image_path = os.path.join(POST_UPLOAD_DIR, file_name)

        # 파일 저장
        with open(new_image_path, "wb") as f:
            f.write(await image_file.read())

        if post.get("image_path") and os.path.exists(post["image_path"]):
            try:
                os.remove(post["image_path"])
            except OSError:
                pass

        post["image_path"] = new_image_path

    # 4) 제목/내용 수정
    post["title"] = title
    post["content"] = content

    return {
        "success": True,
        "message": "게시글이 수정되었습니다.",
        "post": post,
    }