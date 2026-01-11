from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ModerationResult
from app.crud.post_crud import apply_moderation_result

router = APIRouter(prefix="/internal", tags=["internal"])

@router.post("/moderation-result")
def moderation_result(
    body: ModerationResult,
    request: Request,
    db: Session = Depends(get_db),
):
    # agent 서버만 호출 가능
    if request.headers.get("X-Internal-Call") != "true":
        raise HTTPException(status_code=403, detail="Forbidden")

    apply_moderation_result(
        db=db,
        target_type=body.target_type,
        target_id=body.target_id,
        action=body.action,
        reason=body.reason,
    )

    return {"success": True}

