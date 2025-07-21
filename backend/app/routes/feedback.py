from datetime import datetime
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

feedback_router = APIRouter()

class Feedback(BaseModel):
    session_id: str
    question: str
    answer: str
    feedback: str  # "thumbs_up" or "thumbs_down"
    comment: str = ""

@feedback_router.post("/feedback")
async def collect_feedback(feedback: Feedback):
    try:
        if feedback.feedback not in ["thumbs_up", "thumbs_down"]:
            raise HTTPException(status_code=400, detail="Invalid feedback value")
        feedback_entry = feedback.model_dump(mode="json")
        feedback_entry["timestamp"] = datetime.now().isoformat()

        with open("feedback_log.json", "a") as f:
            f.write(json.dumps(feedback_entry) + "\n")

        return {"message": "Feedback recorded"}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
