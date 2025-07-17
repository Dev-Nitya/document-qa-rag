from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from backend.app.config import OPENAI_API_KEY

persist_directory = "chroma_db"

def get_vector_store():
    embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
    vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    return vectordb

def add_documents(docs):
    vectordb = get_vector_store()
    vectordb.add_documents(docs)
    vectordb.persist()