"""Локальный мозг на базе Ollama (Llama 3.2)."""

import requests
from typing import Dict

from . import config


def analyze(user_message: str) -> Dict[str, str]:
    """Отправляет сообщение в Ollama и получает анализ."""
    payload = {
        "model": "llama3.2",
        "prompt": f"Analyze user message and respond as JSON with emotion_detected, importance, action_needed, response_tone. Message: {user_message}",
    }
    try:
        response = requests.post(config.OLLAMA_URL, json=payload, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException:
        # При ошибке возвращаем базовый анализ
        return {
            "emotion_detected": "нейтрально",
            "importance": "низкая",
            "action_needed": "ничего",
            "response_tone": "спокойный",
        }
