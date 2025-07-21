from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.chains.question_answering import load_qa_chain
from backend.app.config import OPENAI_API_KEY

_qa_chain = None
persist_directory = "chroma_db"

REDIS_URL = "redis://localhost:6379/0"

def get_memory(session_id: str):
    message_history = RedisChatMessageHistory(
        url=REDIS_URL,
        session_id=session_id
    )
    memory = ConversationBufferMemory(
        chat_memory=message_history,
        return_messages=True,
        memory_key="chat_history",
        output_key="answer"
    )
    return memory

def build_embeddings():
    return OpenAIEmbeddings()

def get_retriever():
    vectordb = Chroma(
        persist_directory=persist_directory,
        embedding_function=build_embeddings()
    )
    return vectordb.as_retriever(search_kwargs={"k": 3})

def get_qa_chain(session_id: str, prompt: str):
    try:
        # prompt = PromptTemplate.from_template("""
        #     You are a helpful assistant who answers based only on the provided documents.
        #     Use the chat history to provide context if necessary.
        #     If the question cannot be answered based on the docs, say "I don't know".

        #     Answer clearly and concisely.

        #     Chat History:
        #     {chat_history}

        #     Context:
        #     {context}

        #     Question:
        #     {question}
        # """)

        memory = get_memory(session_id)
        retriever = get_retriever()
        llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)

        return ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=True,
            combine_docs_chain_kwargs={"prompt": prompt}
        )
    except Exception as e:
        print(f"Error creating QA chain: {e}")
        raise e