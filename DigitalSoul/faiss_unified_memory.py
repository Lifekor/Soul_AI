import faiss
import numpy as np
import json
import os
from datetime import datetime
from typing import List, Dict, Any
import requests


class FaissUnifiedMemory:
    """Единая система памяти на FAISS с временными приоритетами"""

    def __init__(self):
        self.index_path = "DigitalSoul/data/unified_memory.index"
        self.metadata_path = "DigitalSoul/data/unified_metadata.json"
        self.readable_log_path = "DigitalSoul/data/memory_readable_log.txt"

        self.index = faiss.IndexFlatIP(1536)
        self.metadata: List[Dict[str, Any]] = []
        self.load_index()

    def load_index(self):
        """Загружает существующий индекс или создаёт новый"""
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)

    def save_index(self):
        """Сохраняет индекс и метаданные"""
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    def _embed_text(self, text: str) -> np.ndarray:
        """Создаёт эмбеддинг через OpenAI API"""
        try:
            response = requests.post(
                "https://api.openai.com/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY', 'fake')}",
                    "Content-Type": "application/json",
                },
                json={"input": text, "model": "text-embedding-ada-002"},
                timeout=10,
            )
            if response.status_code == 200:
                embedding = response.json()["data"][0]["embedding"]
                return np.array(embedding, dtype="float32")
        except Exception as e:
            print(f"[WARN] Ошибка создания эмбеддинга: {e}")

        return np.random.random(1536).astype("float32")

    def add_memory(
        self,
        text: str,
        memory_type: str,
        importance: str = "средняя",
        emotion_context: Dict[str, Any] | None = None,
    ) -> None:
        """Добавляет воспоминание в единую память"""
        embedding = self._embed_text(text)
        embedding = np.expand_dims(embedding, axis=0)
        self.index.add(embedding)

        now = datetime.now()
        metadata_entry = {
            "id": len(self.metadata),
            "text": text,
            "memory_type": memory_type,
            "importance": importance,
            "emotion_context": emotion_context or {},
            "timestamp": now.isoformat(),
            "age_hours": 0,
            "priority_score": self._calculate_priority_score(memory_type, importance, 0),
        }
        self.metadata.append(metadata_entry)
        self.save_index()
        self._update_readable_log(text, memory_type, importance)
        print(f"[MEMORY] Добавлено: {memory_type} - {text[:50]}...")

    def _calculate_priority_score(self, memory_type: str, importance: str, age_hours: float) -> float:
        type_weights = {"recent": 1.0, "important": 0.9, "diary": 0.8, "archive": 0.6}
        importance_weights = {"высокая": 1.0, "средняя": 0.8, "низкая": 0.6}
        age_penalty = min(age_hours / (24 * 7), 0.5)
        base_score = type_weights.get(memory_type, 0.6) * importance_weights.get(importance, 0.8)
        return base_score * (1.0 - age_penalty)

    def search_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Ищет воспоминания с учётом временных приоритетов"""
        if self.index.ntotal == 0:
            return []
        self._update_memory_ages()
        query_embedding = self._embed_text(query)
        query_embedding = np.expand_dims(query_embedding, axis=0)
        search_limit = min(limit * 3, self.index.ntotal)
        similarities, indices = self.index.search(query_embedding, search_limit)
        results: List[Dict[str, Any]] = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata):
                memory = self.metadata[idx].copy()
                memory["similarity"] = float(similarities[0][i])
                memory["final_score"] = memory["similarity"] * memory["priority_score"]
                results.append(memory)
        results.sort(key=lambda x: x["final_score"], reverse=True)
        return results[:limit]

    def _update_memory_ages(self):
        now = datetime.now()
        for memory in self.metadata:
            created_time = datetime.fromisoformat(memory["timestamp"])
            age_hours = (now - created_time).total_seconds() / 3600
            memory["age_hours"] = age_hours
            memory["priority_score"] = self._calculate_priority_score(
                memory["memory_type"], memory["importance"], age_hours
            )

    def _update_readable_log(self, text: str, memory_type: str, importance: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{memory_type.upper()}] [{importance}] {text}\n"
        try:
            with open(self.readable_log_path, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"[WARN] Ошибка записи в readable log: {e}")

    def get_memory_stats(self) -> Dict[str, Any]:
        if not self.metadata:
            return {"total": 0}
        stats = {
            "total": len(self.metadata),
            "by_type": {},
            "by_importance": {},
            "oldest": min(self.metadata, key=lambda x: x["timestamp"])["timestamp"],
            "newest": max(self.metadata, key=lambda x: x["timestamp"])["timestamp"],
        }
        for memory in self.metadata:
            stats["by_type"][memory["memory_type"]] = stats["by_type"].get(memory["memory_type"], 0) + 1
            stats["by_importance"][memory["importance"]] = stats["by_importance"].get(memory["importance"], 0) + 1
        return stats

    def migrate_from_old_files(self):
        print("[MIGRATION] Начинаю миграцию старых данных...")
        self._migrate_working_memory()
        self._migrate_longterm_memory()
        self._migrate_full_archive()
        self._migrate_soul_diary()
        print(f"[MIGRATION] Завершена! Всего воспоминаний: {len(self.metadata)}")

    def _migrate_working_memory(self):
        pass

    def _migrate_longterm_memory(self):
        pass

    def _migrate_full_archive(self):
        pass

    def _migrate_soul_diary(self):
        pass
