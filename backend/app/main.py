import os
from fastapi import FastAPI, UploadFile, File
from backend.app.loaders.pdf_loader import load_and_split_documents
from backend.app.utils.vector_store import add_documents
from backend.app.routes.qa import router

app = FastAPI()

app.include_router(router, prefix="/api")

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
