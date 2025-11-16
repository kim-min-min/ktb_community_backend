# app/models/post_model.py
from datetime import datetime
from fastapi import HTTPException

# 임시 저장용 메모리 DB (게시글 + 댓글)
TEMP_POSTS: list[dict] = []
POST_ID_SEQ = 1
COMMENT_ID_SEQ = 1


def get_post_or_404(post_id: int) -> dict:
    """id로 게시글 조회. 없으면 404"""
    for post in TEMP_POSTS:
        if post["id"] == post_id:
            return post
    raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")


def list_posts_desc() -> list[dict]:
    """id 역순으로 전체 게시글 조회"""
    return sorted(TEMP_POSTS, key=lambda x: x["id"], reverse=True)


def create_post(title: str, content: str, image_path: str | None) -> dict:
    """게시글 생성 및 TEMP_POSTS 에 저장"""
    global POST_ID_SEQ

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
    return new_post


def increase_views(post_id: int) -> dict:
    """조회수 +1 후 게시글 반환"""
    post = get_post_or_404(post_id)
    post["views"] += 1
    return post


def toggle_like(post_id: int, liked_now: bool) -> dict:
    """좋아요 토글 후 게시글 반환"""
    post = get_post_or_404(post_id)
    if not liked_now:
        post["likes"] += 1
    else:
        if post["likes"] > 0:
            post["likes"] -= 1
    return post


def add_comment(post_id: int, content: str, writer: str | None = None) -> dict:
    """댓글 추가 후 (post, comment) 를 dict 로 반환"""
    global COMMENT_ID_SEQ
    post = get_post_or_404(post_id)

    comment = {
        "id": COMMENT_ID_SEQ,
        "writer": writer or "더미 작성자 1",
        "content": content,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    post["comments"].append(comment)
    COMMENT_ID_SEQ += 1

    return {
        "post": post,
        "comment": comment,
    }


def update_comment(post_id: int, comment_id: int, content: str) -> dict:
    """댓글 내용 수정 후 수정된 comment 반환"""
    post = get_post_or_404(post_id)

    for c in post["comments"]:
        if c["id"] == comment_id:
            c["content"] = content
            return c

    raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")


def delete_comment(post_id: int, comment_id: int) -> int:
    """댓글 삭제 후 남은 댓글 개수 반환"""
    post = get_post_or_404(post_id)

    before = len(post["comments"])
    post["comments"] = [c for c in post["comments"] if c["id"] != comment_id]
    after = len(post["comments"])

    if before == after:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")

    return after


def update_post(post_id: int, title: str, content: str,
                new_image_path: str | None) -> dict:
    """게시글 제목/내용/이미지 경로 수정"""
    post = get_post_or_404(post_id)

    post["title"] = title
    post["content"] = content
    if new_image_path is not None:
        post["image_path"] = new_image_path

    return post
