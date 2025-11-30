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
    db.add(user)         # INSERT 준비
    db.commit()          # 실제 DB에 반영
    db.refresh(user)     # 방금 INSERT된 값 다시 읽어오기
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    """이메일로 유저 한 명 조회 (SELECT)"""
    return db.query(User).filter(User.email == email).first()


def is_nickname_duplicated(
    db: Session,
    nickname: str,
    exclude_email: str | None = None,
) -> bool:
    """닉네임 중복 여부 (본인 제외 옵션 포함)"""
    q = db.query(User).filter(User.nickname == nickname)
    if exclude_email:
        q = q.filter(User.email != exclude_email)
    return db.query(q.exists()).scalar()


def delete_user_by_email(db: Session, email: str) -> User | None:
    """이메일로 유저 삭제하고, 삭제된 유저 반환"""
    user = get_user_by_email(db, email)
    if user:
        db.delete(user)   # DELETE
        db.commit()
    return user


def update_user_password(
    db: Session,
    email: str,
    new_password: str,
) -> User | None:
    """비밀번호 변경"""
    user = get_user_by_email(db, email)
    if user:
        user.password = new_password   # UPDATE 대상 변경
        db.commit()                    # 실제 반영
        db.refresh(user)               # 최신 상태로 갱신
    return user



def update_user_profile(
    db: Session,
    user: User,
    nickname: str,
    profile_image_path: str | None
) -> User:
    user.nickname = nickname
    if profile_image_path is not None:
        user.profile_image_path = profile_image_path

    db.commit()
    db.refresh(user)
    return user
