"""Облачный мозг на базе OpenAI GPT-4o."""

import os
import requests
from typing import Any, Dict, List

from . import config

OPENAI_URL = "https://api.openai.com/v1/chat/completions"


def generate_response(user_message: str, analysis: Dict[str, Any], memories: List[str]) -> str:
    """Генерирует ответ GPT-4o с учетом анализа и воспоминаний."""
    headers = {
        "Authorization": f"Bearer {config.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    messages = [
        {"role": "system", "content": "You are a friendly AI companion."},
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": f"Context memories: {memories}. Emotion: {analysis.get('emotion_detected')}"},
    ]
    payload = {
        "model": config.OPENAI_MODEL,
        "messages": messages,
    }
    try:
        response = requests.post(OPENAI_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except requests.RequestException:
        return "Извините, нет связи с облачным мозгом."
