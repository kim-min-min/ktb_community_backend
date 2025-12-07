from sqlalchemy import Column, String, Integer
from app.database import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # PK
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    nickname = Column(String(255), unique=True, nullable=False)
    profile_image_path = Column(String(255), nullable=True)

    # 유저 삭제 시, 이 유저의 게시글/댓글도 같이 삭제
    posts = relationship(
        "Post",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,   
    )

    comments = relationship(
        "Comment",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )