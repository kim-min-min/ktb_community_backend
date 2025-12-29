# app/main.py
from fastapi import FastAPI
from app.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth_router import router as auth_router
from app.routes.post_router import router as post_router
from app.routes.internal_router import router as internal_router
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator

# 테이블 자동 생성용
from app.models.user_model import User   

app = FastAPI()


origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MySQL에 테이블 자동 생성
Base.metadata.create_all(bind=engine)

# 라우터 등록
app.include_router(auth_router)
app.include_router(post_router)
app.include_router(internal_router)

# Instrumentator 장착 
Instrumentator().instrument(app).expose(app)


app.mount(
    "/post_uploads",                 # URL prefix
    StaticFiles(directory="post_uploads"),  # 실제 폴더 경로
    name="post_uploads"
)

app.mount(
    "/uploads",                      # URL prefix
    StaticFiles(directory="uploads"),  # 실제 폴더 경로
    name="uploads"
)
