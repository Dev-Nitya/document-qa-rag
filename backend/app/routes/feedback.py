from datetime import datetime
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.utils.db import SessionLocal
from backend.app.models.chat import Feedback, ChatMessage

feedback_router = APIRouter()

class FeedbackRequest(BaseModel):
    session_id: str
    question: str
    answer: str
    feedback: str  # "thumbs_up" or "thumbs_down"
    comment: str = ""
    run_id: str = None  # Optional run_id for tracking

@feedback_router.post("/feedback")
async def collect_feedback(feedback: FeedbackRequest):
    try:
        if feedback.feedback not in ["thumbs_up", "thumbs_down"]:
            raise HTTPException(status_code=400, detail="Invalid feedback value")

        db = SessionLocal()
        feedback_entry = Feedback(
            session_id=feedback.session_id,
            question=feedback.question,
            answer=feedback.answer,
            feedback=feedback.feedback,
            comment=feedback.comment,
            run_id=feedback.run_id
        )
        db.add(feedback_entry)
        db.commit()
        db.refresh(feedback_entry)

        return {"message": "Feedback recorded"}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

    finally:
        db.close()