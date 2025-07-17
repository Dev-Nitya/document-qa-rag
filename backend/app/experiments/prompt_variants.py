from langchain.prompts import ChatPromptTemplate

default_prompt = ChatPromptTemplate.from_template(
    """Use the following context to anwer the question.
    If you don't know the answer, say you dont know.
    Context:
    {context}

    Question: {question}
    """
)

alternate_prompt = ChatPromptTemplate.from_template(
    """You are a helpful assistant. Answer based only on the context below.

    Context:
    {context}

    Now answer: {question}
    """
)