from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain.chains.retrieval_qa.base import RetrievalQA
from backend.app.config import OPENAI_API_KEY
from backend.app.utils.logger import track_timing

_qa_chain = None
persist_directory = "chroma_db"

@track_timing("Embedding setup time")
def build_embeddings():
    return OpenAIEmbeddings()

def get_retriever():
    vectordb = Chroma(
        persist_directory=persist_directory,
        embedding_function=build_embeddings()
    )
    return vectordb.as_retriever(search_kwargs={"k": 3})

def get_qa_chain(llm_model: str):
    prompt = ChatPromptTemplate.from_template(
        """Use the following context to answer the question.
        If you don't know the answer, say you don't know.

        Context:
        {context}

        Question: {question}
        """
    )

    retriever = get_retriever()
    llm = ChatOpenAI(model=llm_model, temperature=0)

    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True
    )