# app/jobs.py
import os
import requests

from app import models
from app.database import SessionLocal
from app.queue import redis
from app.crud.post_crud import apply_moderation_result

AGENT_BASE_URL = os.getenv("AGENT_BASE_URL", "").rstrip("/")
AI_TIMEOUT_SEC = float(os.getenv("AI_HTTP_TIMEOUT", "10"))

ALLOWED = {"safe", "hidden", "review"}

def run_moderation(target_type: str, target_id: int, content: str):
    lock_key = f"moderation:lock:{target_type}:{target_id}"

    try:
        # Agent URL 없으면 그냥 종료
        if not AGENT_BASE_URL:
            return

        # 1) Agent 호출
        try:
            res = requests.post(
                f"{AGENT_BASE_URL}/moderate",
                json={
                    "target_type": target_type,
                    "target_id": target_id,
                    "content": content,
                },
                headers={"X-Internal-Call": "true"},
                timeout=AI_TIMEOUT_SEC,
            )
            res.raise_for_status()
            data = res.json()

            action = (data.get("action") or data.get("decision") or "review")
            action = str(action).strip().lower()
            if action not in ALLOWED:
                action = "review"

            reason = data.get("reason")

        except Exception as e:
            action = "review"
            reason = f"agent_error: {type(e).__name__}"

        # 2) DB 반영 (CRUD)
        db = SessionLocal()
        try:
            apply_moderation_result(
                db=db,
                target_type=target_type,
                target_id=target_id,
                action=action,
                reason=reason,
            )
        finally:
            db.close()

    finally:
        # 3) 락 해제는 어떤 경우에도
        redis.delete(lock_key)
