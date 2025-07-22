from datetime import datetime
import json
import uuid
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from langchain.callbacks import get_openai_callback
from langchain.callbacks.base import BaseCallbackHandler
from langchain.prompts import PromptTemplate

from backend.app.chains.document_qa_chain import get_qa_chain
from backend.app.utils.db import SessionLocal
from backend.app.models.chat import ChatMessage

QARouter = APIRouter()

class RunIDCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.run_id = None
    
    def on_chain_start(self, serialized, inputs, *, run_id, parent_run_id=None, **kwargs):
        self.run_id = str(run_id)
    
    def on_llm_start(self, serialized, prompts, *, run_id, parent_run_id=None, **kwargs):
        if not self.run_id:
            self.run_id = str(run_id)

class QARequest(BaseModel):
    question: str
    session_id: str

@QARouter.post("/ask")
#@track_timing("QA Chain Execution Time")
async def qa_router(request: QARequest):
    try:
        query = request.question
        session_id = request.session_id
        if not query or not session_id:
            raise HTTPException(status_code=400, detail="Question and session_id are required")

        db = SessionLocal()
        user_message = ChatMessage(
            session_id=session_id,
            role="user",
            content=query,
            timestamp=datetime.now(),
            run_id=None  # run_id will be set by the callback handler
        )
        db.add(user_message)
        db.commit()

        prompt = PromptTemplate.from_template("""
            You are a helpful assistant who answers based only on the provided documents.
            Use the chat history to provide context if necessary.
            If the question cannot be answered based on the docs, say "I don't know".

            Answer clearly and concisely.

            Chat History:
            {chat_history}

            Context:
            {context}

            Question:
            {question}
        """)

        qa_chain = get_qa_chain(session_id, prompt)

        async def generate_response():
            try:
                full_answer = ""
                run_id = None
                source_documents = []
                
                # Create callback handler to capture run_id
                run_id_handler = RunIDCallbackHandler()
                
                # Stream the response from the chain
                async for chunk in qa_chain.astream(
                    {"question": query},
                    config={
                        "metadata": {
                            "session_id": session_id,
                            "timestamp": datetime.now(),
                            "prompt_version": "v1",
                        },
                        "callbacks": [run_id_handler]
                    }
                ):
                    if "answer" in chunk:
                        chunk_text = chunk["answer"]
                        full_answer += chunk_text
                        # Send each chunk as Server-Sent Event format
                        yield f"data: {chunk_text}\n\n"
                    
                    if "source_documents" in chunk:
                        source_documents = chunk["source_documents"]

                    # Get run_id from callback handler
                    run_id = run_id_handler.run_id or str(uuid.uuid4())
                    print(f"Run ID: {run_id}")

                    ai_message = ChatMessage(
                        session_id=session_id,
                        role="assistant",
                        content=full_answer,
                        timestamp=datetime.now(),
                        run_id=run_id  # Store run_id in the message
                    )
                    db.add(ai_message)
                    db.commit()

                # Send run_id as a separate data event for frontend to capture
                yield f"data: [RUN_ID:{run_id}]\n\n"
                yield f"data: [DONE]\n\n"
                
            except Exception as e:
                print(f"QA failed for query: {e}")
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
        
    except Exception as e:
        print(f"QA failed for query: {e}")
        raise HTTPException(status_code=500, detail=f"{e} - An error occurred while processing your request")