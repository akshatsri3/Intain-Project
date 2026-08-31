from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.review_decision import DecisionType


class ReviewDecisionRequest(BaseModel):
    decision: DecisionType
    override_value: Optional[str] = None
    reviewer_note: Optional[str] = None
    ai_suggestion_json: Optional[dict] = None


class ReviewDecisionResponse(BaseModel):
    id: int
    exception_id: int
    reviewer_id: int
    decision: DecisionType
    override_value: Optional[str]
    reviewer_note: Optional[str]
    ai_suggestion_json: Optional[dict]
    decided_at: datetime

    model_config = {"from_attributes": True}
