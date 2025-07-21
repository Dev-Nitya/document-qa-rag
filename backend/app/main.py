import os
import logging
from langserve import add_routes
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.app.loaders.pdf_loader import load_and_split_documents
from backend.app.utils.vector_store import add_documents
from backend.app.chains.document_qa_chain import get_qa_chain
from backend.app.routes.qa import QARouter
from backend.app.routes.feedback import feedback_router
from backend.app.routes.chat import chat_router
from backend.app.experiments.test_chains import ab_runner

logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow specific origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(feedback_router, prefix="/api")
app.include_router(QARouter, prefix="/api")
app.include_router(chat_router, prefix="/api")

# ab_runner()

UPLOAD_DIR = "data/sample_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)

    try:
        chunks = load_and_split_documents(file_location)
    except Exception as e:
        return {"status": "Failed", "error": str(e)}
    
    add_documents(chunks)

    return {"status": "Success", "file_name": file.filename, "chunks": len(chunks)}
