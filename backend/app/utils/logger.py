import logging
import time

logger = logging.getLogger("LLMOpsLogger")
logger.setLevel(logging.INFO)

handler = logging.FileHandler("llm_ops.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(handler)

def track_timing(label):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            logger.info(f"{label} - {func.__name__} took {duration:.4f} seconds")
            return result
        return wrapper
    return decorator