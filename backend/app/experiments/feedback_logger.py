from langsmith.run_trees import add_tags, add_metadata

def log_feedback(run_id, score: int, vector_store: float, user_id: None):
    metadata = {
        "user_feedback": score,
        "vector_similiarity": vector_store,
    }
    if user_id:
        metadata["user_id"] = user_id

    add_metadata(run_id=run_id, metadata=metadata)
    add_tags(run_id=run_id, tags=["feedback", "experiment"])