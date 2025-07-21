import uuid
import time
from langsmith.evaluation import evaluate
from langsmith import Client
from langchain_openai import ChatOpenAI

from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from backend.app.chains.document_qa_chain import get_qa_chain

# Two variants of your chain with different LLMs (or prompts, or temperatures)
variants = {
    "gpt-3.5": get_qa_chain("gpt-3.5-turbo"),
    "gpt-4": get_qa_chain("gpt-4"),
}

def evaluate_chains(question: str, retriever, memory):
    run_id = str(uuid.uuid4())

    chain_a = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0),
        retriever=retriever,
        memory=memory,
        return_source_documents=True
    )

    # Chain B: GPT-4
    chain_b = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(model="gpt-4", temperature=0),
        retriever=retriever,
        memory=memory,
        return_source_documents=True
    )

    start = time.time()
    response_a = chain_a.invoke({"question": question})
    response_b = chain_b.invoke({"question": question})
    end = time.time()

    client = Client()
    client.create_run(
        run_id=run_id,
        inputs={"question": question},
        outputs={
            "gpt-3.5": response_a["answer"],
            "gpt-4": response_b["answer"]
        },
        tags=["A/B", "eval"],
        metadata={
            "chain_a_model": "gpt-3.5-turbo",
            "chain_b_model": "gpt-4",
            "latency_seconds": round(end - start, 2)
        }
    )