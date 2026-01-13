# app/queue.py
import os
from redis import Redis
from rq import Queue

# 환경변수에서 Redis URL 읽기
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Redis 연결 (sync, RQ는 sync 기반)
redis = Redis.from_url(
    REDIS_URL,
    decode_responses=True,   # str로 받기 (json/키 처리 편함)
)

# moderation 전용 큐
moderation_q = Queue(
    name="moderation",
    connection=redis,
    default_timeout=60,     # job 기본 제한 시간 (초)
)
