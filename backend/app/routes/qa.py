from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from langchain.callbacks import get_openai_callback

from backend.app.chains.document_qa_chain import get_qa_chain
from backend.app.utils.logger import track_timing, logger

router = APIRouter()

class QARequest(BaseModel):
    question: str

@router.post("/ask")
#@track_timing("QA Chain Execution Time")
def qa_router(request: QARequest):
    print("Received:", request)
    try:
        query = request.question
        qa_chain = get_qa_chain()

        with get_openai_callback() as cb:
            result = qa_chain.invoke({"query": query})

            logger.info(f"Query: {query}")
            logger.info(f"Answer: {result['result']}")

            sources = result.get("source_documents", [])
            if not sources:
                logger.warning(f"No documents found for query: {query}")
            else:
                logger.info(f"Retrieved {len(sources)} source documents")

            # Token & cost metrics
            logger.info(f"Token Usage - Prompt: {cb.prompt_tokens}, Completion: {cb.completion_tokens}, Total: {cb.total_tokens}, Cost: ${cb.total_cost:.6f}")

        return {
            "answer": result["result"],
            "sources": [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in result["source_documents"]
            ]
        }
    except Exception as e:
        logger.exception(f"QA failed for query: {request.question}")
        raise HTTPException(status_code=500, detail="Internal server error")