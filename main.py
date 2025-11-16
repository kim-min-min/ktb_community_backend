# main.py
from fastapi import FastAPI
from app.routes.auth_router import router as auth_router
from app.routes.post_router import router as post_router

app = FastAPI()

# 라우터 등록
app.include_router(auth_router)  # /auth/...
app.include_router(post_router)  # /posts/...
