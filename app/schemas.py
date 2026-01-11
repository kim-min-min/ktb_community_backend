from pydantic import BaseModel
from typing import Optional, Literal

class ModerationResult(BaseModel):
    target_type: Literal["post", "comment"]
    target_id: int
    action: Literal["safe", "hidden", "review"]
    reason: Optional[str] = None