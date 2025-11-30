# app/main.py
from fastapi import FastAPI
from app.database import Base, engine
from app.routes.auth_router import router as auth_router
from app.routes.post_router import router as post_router

# 테이블 자동 생성용
from app.models.user_model import User   

app = FastAPI()

# MySQL에 테이블 자동 생성
Base.metadata.create_all(bind=engine)

# 라우터 등록
app.include_router(auth_router)
app.include_router(post_router)
