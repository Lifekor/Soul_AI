"""Локальный мозг на базе Ollama (Llama 3.2)."""

import json
import re
from datetime import datetime
import requests
from typing import Any, Dict

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


def analyze_with_self_learning(user_message: str, soul_memory: Dict[str, Any]) -> Dict[str, Any]:
    """Улучшенный анализ с самообучением"""

    learned_patterns = soul_memory.get("emotion_corrections", {})
    for pattern, correct_analysis in learned_patterns.items():
        if pattern.lower() in user_message.lower():
            print(f"[DEBUG] Использую выученный паттерн: {pattern}")
            return correct_analysis

    prompt = f"""Анализируй эмоцию в сообщении: "{user_message}"

ВАЖНЫЕ ПРАВИЛА:
- "не грустно", "уже лучше", "спасибо" = РАДОСТЬ/ОБЛЕГЧЕНИЕ, НЕ грусть!
- "mon amour", "❤️", "<3", "люблю" = НЕЖНОСТЬ/ЛЮБОВЬ, НЕ грусть!
- "привет", "как дела" = importance: низкая
- Личные факты, имена, сильные эмоции = importance: высокая

Определи также подходящий тон для ответа и сабтон:
- радость → игривый тон
- нежность → нежный тон  
- грусть → сочувствующий тон

Ответь СТРОГО в формате:
emotion=радость
importance=средняя
action=запомнить
tone=игривый
subtone=дрожащий"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3.2:3b", "prompt": prompt, "stream": False},
            timeout=10,
        )

        if response.status_code == 200:
            llama_response = response.json().get("response", "")

            result = parse_llama_analysis(llama_response)

            if should_flag_for_correction(user_message, result):
                flag_analysis_for_review(user_message, result, soul_memory)

            return result

    except Exception as e:
        print(f"[WARN] Ошибка анализа Llama: {e}")

    return {
        "emotion_detected": "нейтрально",
        "importance": "низкая",
        "action_needed": "ничего",
        "response_tone": "спокойный",
        "subtone": None,
    }


def call_llama_analysis(prompt: str) -> Dict[str, Any]:
    payload = {"model": "llama3.2:3b", "prompt": prompt, "stream": False}
    try:
        response = requests.post(config.OLLAMA_URL, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json().get("response", "")
        result = {
            "emotion_detected": "нейтрально",
            "importance": "низкая",
            "action_needed": "ничего",
            "response_tone": "спокойный",
        }
        patterns = {
            "emotion_detected": r"emotion=(\w+)",
            "importance": r"importance=(\w+)",
            "action_needed": r"action=(\w+)",
            "response_tone": r"tone=(\w+)",
        }
        for key, rgx in patterns.items():
            m = re.search(rgx, data)
            if m:
                result[key] = m.group(1)
        return result
    except Exception as e:
        print(f"Ошибка анализа Llama: {e}")
        return {
            "emotion_detected": "нейтрально",
            "importance": "низкая",
            "action_needed": "ничего",
            "response_tone": "спокойный",
        }


def should_remember_for_correction(message: str, analysis: Dict[str, Any]) -> bool:
    return analysis.get("importance") == "высокая" and analysis.get("emotion_detected") == "грусть" and "не" in message.lower()


def save_analysis_for_review(message: str, analysis: Dict[str, Any], soul_memory: Dict[str, Any]):
    corrections = soul_memory.setdefault("pending_corrections", [])
    corrections.append({
        "message": message,
        "analysis": analysis,
        "timestamp": datetime.now().isoformat(),
    })


def parse_llama_analysis(response_text: str) -> Dict[str, Any]:
    """Парсит ответ Llama в словарь."""
    result = {
        "emotion_detected": "нейтрально",
        "importance": "низкая",
        "action_needed": "ничего",
        "response_tone": "спокойный",
        "subtone": None,
    }
    patterns = {
        "emotion_detected": r"emotion=([\w-]+)",
        "importance": r"importance=([\w-]+)",
        "action_needed": r"action=([\w-]+)",
        "response_tone": r"tone=([\w-]+)",
        "subtone": r"subtone=([\w\-]+)",
    }
    for key, rgx in patterns.items():
        m = re.search(rgx, response_text)
        if m:
            result[key] = m.group(1)
    return result


def should_flag_for_correction(message: str, analysis: Dict[str, Any]) -> bool:
    return analysis.get("emotion_detected") == "грусть" and "не" in message.lower()


def flag_analysis_for_review(message: str, analysis: Dict[str, Any], soul_memory: Dict[str, Any]):
    pending = soul_memory.setdefault("pending_corrections", [])
    pending.append({
        "message": message,
        "analysis": analysis,
        "timestamp": datetime.now().isoformat(),
    })
