# app/crud/post_crud.py
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.post_model import Post, Comment


# -----------------------------
# 게시글 관련 CRUD
# -----------------------------
def get_post_or_404(db: Session, post_id: int) -> Post:
    """id로 게시글 조회. 없으면 404"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    return post


def list_posts_desc(db: Session) -> list[Post]:
    """id 역순으로 전체 게시글 조회"""
    return db.query(Post).order_by(Post.id.desc()).all()


def create_post(
    db: Session,
    title: str,
    content: str,
    image_path: str | None,
) -> Post:
    """게시글 생성 후 DB 저장"""
    new_post = Post(
        title=title,
        content=content,
        image_path=image_path,
        likes=0,
        views=0,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


def increase_views(db: Session, post_id: int) -> Post:
    """조회수 +1 후 게시글 반환"""
    post = get_post_or_404(db, post_id)
    post.views += 1
    db.commit()
    db.refresh(post)
    return post


def toggle_like(db: Session, post_id: int, liked_now: bool) -> Post:
    """
    좋아요 토글 후 게시글 반환

    liked_now:
      - False → 지금 막 좋아요 누른 상황 → +1
      - True  → 좋아요 해제 → -1 (0 밑으로는 안내려감)
    """
    post = get_post_or_404(db, post_id)

    if not liked_now:
        post.likes += 1
    else:
        if post.likes > 0:
            post.likes -= 1

    db.commit()
    db.refresh(post)
    return post


def update_post(
    db: Session,
    post_id: int,
    title: str,
    content: str,
    new_image_path: str | None,
) -> Post:
    """게시글 제목/내용/이미지 경로 수정"""
    post = get_post_or_404(db, post_id)

    post.title = title
    post.content = content
    if new_image_path is not None:
        post.image_path = new_image_path

    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, post_id: int) -> Post:
    """게시글 삭제 후 삭제된 Post 반환"""
    post = get_post_or_404(db, post_id)  # 없으면 404

    db.delete(post)
    db.commit()
    return post



# -----------------------------
# 댓글 관련 CRUD
# -----------------------------
def add_comment(
    db: Session,
    post_id: int,
    content: str,
    writer: str | None = None,
) -> dict:
    """
    댓글 추가 후 (post, comment) 를 dict 로 반환
    (기존 메모리 버전 인터페이스랑 맞추려고 dict 형태 유지)
    """
    post = get_post_or_404(db, post_id)

    comment = Comment(
        post_id=post.id,
        writer=writer or "더미 작성자 1",
        content=content,
    )
    db.add(comment)
    db.commit()
    db.refresh(post)
    db.refresh(comment)

    return {
        "post": post,
        "comment": comment,
    }


def update_comment(
    db: Session,
    post_id: int,
    comment_id: int,
    content: str,
) -> Comment:
    """댓글 내용 수정 후 수정된 comment 반환"""
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id, Comment.post_id == post_id)
        .first()
    )
    if comment is None:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")

    comment.content = content
    db.commit()
    db.refresh(comment)
    return comment


def delete_comment(db: Session, post_id: int, comment_id: int) -> int:
    """댓글 삭제 후 남은 댓글 개수 반환"""
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id, Comment.post_id == post_id)
        .first()
    )
    if comment is None:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")

    db.delete(comment)
    db.commit()

    # 남은 댓글 개수
    remaining = db.query(Comment).filter(Comment.post_id == post_id).count()
    return remaining
