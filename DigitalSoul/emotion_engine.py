"""Простейший движок эмоций."""

import json
import os
from typing import Dict

from . import config


class EmotionEngine:
    """Управляет текущей эмоцией."""

    def __init__(self):
        self.current_emotion = "нейтрально"
        self.load_from_file()

    def load_from_file(self):
        """Загружает эмоцию из файла."""
        if os.path.exists(config.EMOTIONS_PATH):
            try:
                with open(config.EMOTIONS_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.current_emotion = data.get("current", "нейтрально")
            except Exception:
                pass

    def update(self, detected: str) -> None:
        """Обновляет текущую эмоцию и сохраняет её."""
        self.current_emotion = detected
        self.save_to_file()

    def save_to_file(self):
        """Сохраняет текущую эмоцию."""
        try:
            with open(config.EMOTIONS_PATH, "w", encoding="utf-8") as f:
                json.dump({"current": self.current_emotion}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения эмоции: {e}")

    def influence_tone(self, text: str) -> str:
        """Добавляет эмоцию в текст."""
        if self.current_emotion == "радость":
            return text + " 😊"
        if self.current_emotion == "грусть":
            return text + " 😔"
        if self.current_emotion == "любопытство":
            return text + " ❓"
        if self.current_emotion == "нежность":
            return text + " 💖"
        return text
