import os
from fastapi import APIRouter, UploadFile, File
from backend.app.loaders.pdf_loader import load_and_split_documents
from backend.app.utils.vector_store import add_documents
from backend.app.chains.document_qa_chain import get_qa_chain

upload_router = APIRouter()

UPLOAD_DIR = "data/sample_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@upload_router.post("/upload")
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