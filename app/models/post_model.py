from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timedelta, timezone


KST = timezone(timedelta(hours=9))

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    image_path = Column(String(255), nullable=True)
    likes = Column(Integer, default=0)
    views = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(KST))

    # agent용 추가
    moderation_status = Column(String(20), default="PENDING", nullable=False)
    moderation_reason = Column(String(255), nullable=True)

    # 글쓴이 (User FK)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # 관계 설정 (User ↔ Post)
    user = relationship("User", back_populates="posts")

    # 댓글 리스트 (1 : N)
    comments = relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete-orphan"
    )
    


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"))

    # 댓글 작성자 (User FK)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # 화면에 보여줄 닉네임
    writer = Column(String(50), nullable=False)

    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(KST))

    # 관계
    # Comment.post → Post
    post = relationship("Post", back_populates="comments")

    # Comment.user → User
    user = relationship("User", back_populates="comments")
