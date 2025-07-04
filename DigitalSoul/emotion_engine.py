"""Простейший движок эмоций."""

from typing import Dict


class EmotionEngine:
    """Управляет текущей эмоцией."""

    def __init__(self):
        self.current_emotion = "нейтрально"

    def update(self, detected: str) -> None:
        """Обновляет текущую эмоцию."""
        self.current_emotion = detected

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
