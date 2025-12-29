from pydantic import BaseModel
from typing import Optional


class ModerationResult(BaseModel):
    post_id: int
    action: str          # 예: "DELETE", "BLOCK", "ALLOW"
    reason: Optional[str] = None
