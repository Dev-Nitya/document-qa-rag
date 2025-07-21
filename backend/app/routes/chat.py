from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import StreamingResponse, JSONResponse
from uuid import uuid4
from pydantic import BaseModel
from langchain.prompts import PromptTemplate

from backend.app.chains.document_qa_chain import get_qa_chain

chat_router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    session_id: str = None  # Optional

@chat_router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    session_id = request.session_id or str(uuid4())

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
            
        except Exception as e:
            yield f"data: [ERROR: {str(e)}]\n\n"

    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )