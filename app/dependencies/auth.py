from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer  
from sqlalchemy.orm import Session
from jose import JWTError

from app.core.security import decode_access_token
from app.database import get_db
from app.models.user_model import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:

    try:
        payload = decode_access_token(token)  # ← 여기서 exp + signature 검증
        user_id = payload.get("sub")

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 유효하지 않거나 만료되었습니다.",
        )

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="토큰에 포함된 사용자 정보 없음",
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=401,
            detail="사용자를 찾을 수 없음",
        )

    return user
