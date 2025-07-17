import os
from backend.app.loaders.pdf_loader import load_and_split_documents

def test_load_and_split_documents():
    test_pdf_path = os.path.join(os.path.dirname(__file__), 'data', 'sample.pdf')
    chunks = load_and_split_documents(test_pdf_path)
    
    assert len(chunks) > 0