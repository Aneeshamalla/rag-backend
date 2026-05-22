import os
from dotenv import load_dotenv
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("INDEX_NAME", "rag-index")

GROQ_API_KEY = os.getenv("GROQ_API_KEY") 
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3-70b-8192")

# Fail fast with a clear message if critical keys are missing
_required = {"PINECONE_API_KEY": PINECONE_API_KEY, "GROQ_API_KEY": GROQ_API_KEY}
for _name, _val in _required.items():
    if not _val:
        raise RuntimeError(f"Missing required environment variable: {_name}")