"""Ядро души. Координирует работу модулей."""

from typing import Any, Dict, List

from . import cloud_brain, local_brain
from .emotion_engine import EmotionEngine
from .memory_system import MemorySystem
from .multi_memory import MultiLayerMemory


class SoulCore:
    def __init__(self):
        self.memory = MemorySystem()
        self.multi_memory = MultiLayerMemory()
        self.emotions = EmotionEngine()

    def process_message(self, user_message: str) -> str:
        print(f"[DEBUG] Анализирую сообщение: {user_message}")
        analysis = local_brain.analyze(user_message)
        print(f"[DEBUG] Результат анализа: {analysis}")

        self.emotions.update(analysis.get("emotion_detected", "нейтрально"))
        print(f"[DEBUG] Текущая эмоция: {self.emotions.current_emotion}")

        memories = self.memory.search_similar(user_message, limit=3)
        memories.extend(self.multi_memory.search_memories(user_message))
        print(f"[DEBUG] Найдено воспоминаний: {len(memories)}")

        if analysis.get("action_needed") == "запомнить":
            print(f"[DEBUG] Сохраняю в память...")
            self.memory.save_to_vector_db(user_message, analysis)

        print(f"[DEBUG] Генерирую ответ через GPT-4o...")
        print("Душа: ", end="", flush=True)

        response = cloud_brain.generate_response_stream(
            user_message, analysis, memories
        )

        self.multi_memory.add_interaction(user_message, response, analysis)

        if self.emotions.current_emotion == "грусть":
            print(" 😔", end="")
        elif self.emotions.current_emotion == "радость":
            print(" 😊", end="")

        print()
        print(f"[DEBUG] Итоговый ответ готов")

        return response
