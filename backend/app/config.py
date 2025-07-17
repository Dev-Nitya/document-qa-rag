import os
from dotenv import load_dotenv
from pathlib import Path

# Get the directory of this config.py file
current_dir = Path(__file__).parent

# Load .env file from the same directory as config.py
env_path = current_dir / '.env'
load_dotenv(env_path)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")