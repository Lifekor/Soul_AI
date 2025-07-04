"""Система памяти на базе FAISS."""

import json
import os
from datetime import datetime
from typing import Any, Dict, List

import faiss
import numpy as np
import requests

from . import config


class MemorySystem:
    """Простая векторная память."""

    def __init__(self):
        self.index = faiss.IndexFlatIP(1536)
        self.metadata: List[Dict[str, Any]] = []
        if os.path.exists(config.FAISS_INDEX_PATH):
            self.index = faiss.read_index(config.FAISS_INDEX_PATH)
        if os.path.exists(config.METADATA_PATH):
            with open(config.METADATA_PATH, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)

    # ------------------------------------------------------------------
    # Memory saving helpers
    # ------------------------------------------------------------------
    def should_save_to_memory(self, text: str, analysis: Dict[str, Any]) -> bool:
        """Определяет, стоит ли сохранять сообщение в память."""
        if len(text) > 500:
            return False

        importance = analysis.get("importance", "низкая")
        if importance in ["высокая", "средняя"]:
            return True

        personal_keywords = [
            "зовут",
            "имя",
            "работаю",
            "живу",
            "люблю",
            "ненавижу",
        ]
        if any(keyword in text.lower() for keyword in personal_keywords):
            return True

        return False

    def _embed(self, text: str) -> np.ndarray:
        """Получение эмбеддинга через OpenAI."""
        headers = {
            "Authorization": f"Bearer {config.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "input": text,
            "model": config.EMBEDDING_MODEL,
        }
        response = requests.post(
            "https://api.openai.com/v1/embeddings", headers=headers, json=payload
        )
        response.raise_for_status()
        vec = np.array(response.json()["data"][0]["embedding"], dtype="float32")
        return vec

    def search_similar(self, text: str, limit: int = 3) -> List[str]:
        if self.index.ntotal == 0:
            return []
        vec = self._embed(text)
        vec = np.expand_dims(vec, axis=0)
        scores, ids = self.index.search(vec, limit)
        results = []
        for i in ids[0]:
            if i < len(self.metadata):
                results.append(self.metadata[i]["text"])
        return results

    def save_to_vector_db(self, text: str, analysis: Dict[str, Any]):
        if not self.should_save_to_memory(text, analysis):
            return

        if len(self.metadata) >= 100:
            self.metadata = self.metadata[-90:]
            self.index = faiss.IndexFlatIP(1536)
            for item in self.metadata:
                vec = self._embed(item["text"])
                vec = np.expand_dims(vec, axis=0)
                self.index.add(vec)

        vec = self._embed(text)
        vec = np.expand_dims(vec, axis=0)
        self.index.add(vec)
        self.metadata.append(
            {
                "text": text,
                "analysis": analysis,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        faiss.write_index(self.index, config.FAISS_INDEX_PATH)
        with open(config.METADATA_PATH, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
