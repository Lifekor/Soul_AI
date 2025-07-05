# Конфигурация проекта Digital Soul

OLLAMA_URL = "http://localhost:11434/api/generate"
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o"
EMBEDDING_MODEL = "text-embedding-ada-002"
FAISS_INDEX_PATH = "DigitalSoul/data/vector_memory.index"
METADATA_PATH = "DigitalSoul/data/memory_metadata.json"
EMOTIONS_PATH = "DigitalSoul/data/emotions.json"
PERSONALITY_PATH = "DigitalSoul/data/personality.json"

# Paths for the multi-layer memory system
MEMORY_DIR = "DigitalSoul/data/memory"
WORKING_MEMORY_PATH = f"{MEMORY_DIR}/working_memory.json"
LONGTERM_MEMORY_PATH = f"{MEMORY_DIR}/longterm_memory.json"
PERSONAL_FACTS_PATH = f"{MEMORY_DIR}/personal_facts.json"
FULL_ARCHIVE_PATH = f"{MEMORY_DIR}/full_archive.jsonl"
SOUL_DIARY_PATH = f"{MEMORY_DIR}/soul_diary.json"
