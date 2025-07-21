# For LangSmith tracing
from langsmith.client import Client
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

def ab_runner():
    prompt = PromptTemplate.from_template("""
    You are a helpful assistant who answers user questions. If you dont know the answer, say "I don't know".
    """)

    chain_a = prompt | ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    chain_b = prompt | ChatOpenAI(model="gpt-4", temperature=0)

    questions = [
        "What is the capital of France?",
        "What is the most populous country in the world?",
    ]

    results = []

    for q in questions:
        input_dict = {"question": q}

        output_a = chain_a.invoke(
            input_dict,
            config={
                "run_name": "ChainA-v1",
                "tags": ["ab-test", "version-1"],
                "metadata": {"experiment": "ab_test_july21"},
                "project_name": "Smart QA A/B Test"
            }
        )

        output_b = chain_b.invoke(
            input_dict,
            config={
                "run_name": "ChainB-v2",
                "tags": ["ab-test", "version-2"],
                "metadata": {"experiment": "ab_test_july21"},
                "project_name": "Smart QA A/B Test"
            }
        )

        results.append({
            "question": q,
            "chainA": output_a,
            "chainB": output_b
        })
