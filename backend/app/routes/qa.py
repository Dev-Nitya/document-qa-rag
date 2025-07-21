import datetime
import json
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from langchain.callbacks import get_openai_callback
from langchain.prompts import PromptTemplate

from backend.app.chains.document_qa_chain import get_qa_chain
from backend.app.utils.logger import track_timing, logger

QARouter = APIRouter()

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
                source_documents = []
                
                # Stream the response from the chain
                async for chunk in qa_chain.astream(
                    {"question": query},
                    config={
                        "metadata": {
                            "session_id": session_id,
                            "timestamp": datetime.datetime.now().isoformat(),
                            "prompt_version": "v1",
                        }
                    }
                ):
                    if "answer" in chunk:
                        chunk_text = chunk["answer"]
                        full_answer += chunk_text
                        # Send each chunk as Server-Sent Event format
                        yield f"data: {chunk_text}\n\n"
                    
                    if "source_documents" in chunk:
                        source_documents = chunk["source_documents"]

                # Log the complete interaction
                log_data = {
                    "session_id": session_id,
                    "question": query,
                    "answer": full_answer,
                    "source_documents": [doc.page_content for doc in source_documents] if source_documents else [],
                    "timestamp": datetime.datetime.now().isoformat()
                }
                with open("qa_log.json", "a") as log_file:
                    log_file.write(json.dumps(log_data) + "\n")

                # Send sources at the end
                # if source_documents:
                #     sources_data = json.dumps({
                #         "sources": [
                #             {
                #                 "content": doc.page_content,
                #                 "metadata": doc.metadata
                #             }
                #             for doc in source_documents
                #         ]
                #     })
                #     yield f"data: [SOURCES:{sources_data}]\n\n"
                
                yield f"data: [DONE]\n\n"
                
            except Exception as e:
                print(f"QA failed for query: {e}")
                yield f"data: [ERROR: {str(e)}]\n\n"

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