from langsmith.evaluation import evaluate
from langsmith import Client

from backend.app.chains.document_qa_chain import get_qa_chain

# Two variants of your chain with different LLMs (or prompts, or temperatures)
variants = {
    "gpt-3.5": get_qa_chain("gpt-3.5-turbo"),
    "gpt-4": get_qa_chain("gpt-4"),
}

# Example test questions (inputs)
dataset = [
    {"query": "What are the symptoms of Vitamin D deficiency?"},
    {"query": "Explain how generative AI works in simple terms."},
]

def correctness(prediction: str, query: str):
    return {"contains_query": query.lower() in prediction.lower()}

client = Client()

results = evaluate(
    target=list(variants.values()),
    data=dataset,
    evaluators=[correctness],
    summary_evaluators=None,
    experiment_prefix="QA-prompt-A-vs-B"
)
print(results.experiment_name)