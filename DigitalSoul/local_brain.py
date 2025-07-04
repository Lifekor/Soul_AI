"""Локальный мозг на базе Ollama (Llama 3.2)."""

import json
import re
import requests
from typing import Dict

from . import config


def analyze(user_message: str) -> Dict[str, str]:
    """Анализирует сообщение пользователя через Llama 3.2."""

    prompt = f"""Анализируй эмоцию пользователя в сообщении: "{user_message}"

Ответь точно в таком формате:
emotion=грусть
importance=высокая
action=запомнить
tone=сочувствующий

Возможные эмоции: радость, грусть, злость, страх, нейтрально, любопытство, нежность
Важность: низкая, средняя, высокая
Действие: запомнить, ничего
Тон ответа: игривый, нежный, серьезный, сочувствующий, спокойный"""

    payload = {
        "model": "llama3.2:3b",
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(config.OLLAMA_URL, json=payload, timeout=10)
        response.raise_for_status()
        ollama_data = response.json()
        llama_response = ollama_data.get("response", "")

        result = {
            "emotion_detected": "нейтрально",
            "importance": "низкая",
            "action_needed": "ничего",
            "response_tone": "спокойный",
        }

        emotion_match = re.search(r"emotion=(\w+)", llama_response)
        if emotion_match:
            result["emotion_detected"] = emotion_match.group(1)

        importance_match = re.search(r"importance=(\w+)", llama_response)
        if importance_match:
            result["importance"] = importance_match.group(1)

        action_match = re.search(r"action=(\w+)", llama_response)
        if action_match:
            result["action_needed"] = action_match.group(1)

        tone_match = re.search(r"tone=(\w+)", llama_response)
        if tone_match:
            result["response_tone"] = tone_match.group(1)

        return result

    except Exception as e:
        print(f"Ошибка анализа Llama: {e}")
        return {
            "emotion_detected": "нейтрально",
            "importance": "низкая",
            "action_needed": "ничего",
            "response_tone": "спокойный",
        }


def analyze_extended(user_message: str) -> Dict[str, str]:
    """Расширенный анализ с тонами, сабтонами и флейворами."""

    prompt = f"""Проанализируй сообщение пользователя: "{user_message}"

Определи:
1. Основную эмоцию: радость, грусть, злость, страх, нейтрально, любопытство, нежность, тревога
2. Тон ответа: нежный, игривый, серьезный, сочувствующий, спокойный, страстный, уязвимый, заботливый
3. Сабтон (если нужен): шепчущий, дрожащий, уверенный, мечтательный, задумчивый, обнадеживающий, интимный
4. Флейвор (атмосфера): тепло-обволакивающий, легко-игривый, глубоко-философский, мягко-поддерживающий, ярко-вдохновляющий

Ответь в формате:
emotion=грусть
tone=сочувствующий
subtone=дрожащий
flavor=тепло-обволакивающий
importance=высокая
action=запомнить"""

    payload = {
        "model": "llama3.2:3b",
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(config.OLLAMA_URL, json=payload, timeout=10)
        response.raise_for_status()
        ollama_data = response.json()
        llama_response = ollama_data.get("response", "")

        result = {
            "emotion": "нейтрально",
            "tone": "спокойный",
            "subtone": None,
            "flavor": None,
            "importance": "низкая",
            "action": "ничего",
        }

        patterns = {
            "emotion": r"emotion=(\w+)",
            "tone": r"tone=(\w+)",
            "subtone": r"subtone=(\w+)",
            "flavor": r"flavor=([\w\-]+)",
            "importance": r"importance=(\w+)",
            "action": r"action=(\w+)",
        }

        for key, regex in patterns.items():
            match = re.search(regex, llama_response)
            if match:
                result[key] = match.group(1)

        return result

    except Exception as e:
        print(f"Ошибка анализа Llama: {e}")
        return {
            "emotion": "нейтрально",
            "tone": "спокойный",
            "subtone": None,
            "flavor": None,
            "importance": "низкая",
            "action": "ничего",
        }
