from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path
from langchain.callbacks.tracers import LangChainTracer
from langsmith import traceable
from backend.app.config import OPENAI_API_KEY

tracer = LangChainTracer(project_name="smart-doc-qa-rag")

@traceable(name="PDF Load and Split Test Run")
def load_and_split_documents(file_path: str):
    ext = Path(file_path).suffix.lower()
    if ext == '.pdf':
        loader = PyPDFLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(documents)

    return chunks