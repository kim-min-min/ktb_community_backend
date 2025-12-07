# app/crud/user_crud.py
from sqlalchemy.orm import Session
from app.models.user_model import User  # ORM 모델


def create_user(
    db: Session,
    email: str,
    password: str,
    nickname: str,
    profile_image_path: str | None = None,
) -> User:
    """회원 생성 (DB INSERT)"""
    user = User(
        email=email,
        password=password,
        nickname=nickname,
        profile_image_path=profile_image_path,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    """이메일로 유저 한 명 조회 (SELECT)"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """id로 유저 한 명 조회"""
    return db.query(User).filter(User.id == user_id).first()


def is_nickname_duplicated(
    db: Session,
    nickname: str,
    exclude_user_id: int | None = None,
) -> bool:
    """닉네임 중복 여부 (본인 제외 옵션 포함, id 기준)"""
    q = db.query(User).filter(User.nickname == nickname)
    if exclude_user_id is not None:
        q = q.filter(User.id != exclude_user_id)
    return db.query(q.exists()).scalar()


def delete_user(db: Session, user: User) -> User:
    """User 객체를 받아서 삭제"""
    db.delete(user)
    db.commit()
    return user


def update_user_password(
    db: Session,
    user: User,
    new_hashed_password: str,
) -> User:
    """비밀번호 변경 (이미 해시된 비밀번호 사용)"""
    user.password = new_hashed_password
    db.commit()
    db.refresh(user)
    return user


def update_user_profile(
    db: Session,
    user: User,
    nickname: str,
    profile_image_path: str | None
) -> User:
    """닉네임 / 프로필 이미지 경로 수정"""
    user.nickname = nickname
    if profile_image_path is not None:
        user.profile_image_path = profile_image_path

    db.commit()
    db.refresh(user)
    return user
