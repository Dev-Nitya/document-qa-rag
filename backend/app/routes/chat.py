from datetime import datetime
from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import StreamingResponse, JSONResponse
from uuid import uuid4
from pydantic import BaseModel
from langchain.prompts import PromptTemplate

from backend.app.chains.document_qa_chain import get_qa_chain
from backend.app.utils.db import SessionLocal
from backend.app.models.chat import ChatSession, ChatMessage

chat_router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    session_id: str = None  # Optional

@chat_router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    session_id = request.session_id or str(uuid4())

    db = SessionLocal()
    chat_session = ChatSession(id=session_id)
    db.add(chat_session)
    db.commit()

    prompt = PromptTemplate.from_template("""
            You are a helpful assistant who answers the user based on his question.
            The question would most likely be a greeting, so you can respond accordingly.
            {question}
            Context: {context}
        """)

    chain = get_qa_chain(session_id, prompt)
    
    async def generate_response():
        try:
            # Stream the response from the chain
            async for chunk in chain.astream({"question": request.question}):
                if "answer" in chunk:
                    # Send each chunk as Server-Sent Event format
                    yield f"data: {chunk['answer']}\n\n"
            
            # Send session_id at the end
            yield f"data: [SESSION_ID:{session_id}]\n\n"
            yield f"data: [DONE]\n\n"

            ai_message = ChatMessage(
                session_id=session_id,
                role="assistant",
                content=chunk.get("answer", ""),
                timestamp=datetime.now(),
                run_id="dummy_run_id"  # Placeholder for run_id
            )
            db.add(ai_message)
            db.commit()
            
        except Exception as e:
            yield f"data: [ERROR: {str(e)}]\n\n"

        finally:
            db.close()

    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )