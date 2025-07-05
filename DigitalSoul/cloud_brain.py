"""Облачный мозг с поддержкой многослойных эмоций."""

import json
import requests
from typing import Any, Dict, List

from . import config

OPENAI_URL = "https://api.openai.com/v1/chat/completions"


def generate_response_with_emotional_layers(
    user_message: str, analysis: Dict[str, Any], memories: List[str]
) -> str:
    """Генерирует ответ с полной эмоциональной системой, учитывая триггеры."""

    tone_data = load_emotional_data()
    trigger_data = load_trigger_phrases()

    # Сначала проверяем наличие триггера
    trigger_result = check_trigger_phrases(user_message, trigger_data)

    if trigger_result.get("triggered"):
        current_tone = trigger_result.get("tone")
        current_subtone = trigger_result.get("subtone")
        current_flavor = trigger_result.get("flavor")
        current_emotion = trigger_result.get("emotion")
        inspiration = trigger_result.get("inspiration")
        print(
            f"[DEBUG] Триггер активирован: тон={current_tone}, сабтон={current_subtone}, флейвор={current_flavor}"
        )
    else:
        current_emotion = analysis.get("emotion_detected", "нейтрально")
        current_tone = determine_tone_from_emotion(current_emotion)
        current_subtone = select_compatible_subtone(current_tone, tone_data)
        current_flavor = select_compatible_flavor(current_tone, tone_data)
        inspiration = None
        print(
            f"[DEBUG] Эмоции из анализа: эмоция={current_emotion}, тон={current_tone}"
        )

    print(
        f"[DEBUG] Финальное состояние: тон={current_tone}, сабтон={current_subtone}, флейвор={current_flavor}"
    )

    tone_examples = get_tone_examples(current_tone, tone_data)
    subtone_examples = (
        get_subtone_examples(current_subtone, tone_data) if current_subtone else []
    )
    flavor_examples = (
        get_flavor_examples(current_flavor, tone_data) if current_flavor else []
    )

    system_prompt = create_living_prompt_with_examples(
        emotion=current_emotion,
        tone_examples=tone_examples,
        subtone_examples=subtone_examples,
        flavor_examples=flavor_examples,
        memories=memories,
        inspiration=inspiration,
    )

    temperature = calculate_emotional_temperature(
        current_emotion, current_tone, current_subtone
    )

    return call_gpt4_with_full_context(system_prompt, user_message, temperature)


def load_emotional_data():
    """Загружает всю эмоциональную систему"""
    try:
        with open("DigitalSoul/data/tone_memory.json", "r", encoding="utf-8") as f:
            tones = json.load(f)
        with open("DigitalSoul/data/subtone_memory.json", "r", encoding="utf-8") as f:
            subtones = json.load(f)
        with open("DigitalSoul/data/flavor_memory.json", "r", encoding="utf-8") as f:
            flavors = json.load(f)
        return {"tones": tones.get("available_tones", {}), "subtones": subtones.get("available_subtones", {}), "flavors": flavors.get("available_flavors", {})}
    except Exception as e:
        print(f"[WARN] Ошибка загрузки эмоций: {e}")
        return {"tones": {}, "subtones": {}, "flavors": {}}


def load_trigger_phrases():
    try:
        with open("DigitalSoul/data/trigger_phrases.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"phrases": []}


def check_trigger_phrases(user_message: str, triggers: dict) -> dict:
    """Проверяет триггер-фразы и возвращает эмоциональное состояние."""
    for trigger_data in triggers.get("phrases", []):
        if trigger_data["trigger"].lower() in user_message.lower():
            return {
                "triggered": True,
                "tone": trigger_data.get("tone", "спокойный"),
                "subtone": trigger_data.get("subtone"),
                "flavor": trigger_data.get("flavor"),
                "emotion": trigger_data.get("emotion", ["нейтрально"])[0],
                "inspiration": trigger_data.get("response", ""),
            }
    return {"triggered": False}


def determine_tone_from_emotion(emotion: str) -> str:
    """Определяет подходящий тон на основе эмоции."""
    emotion_to_tone = {
        "радость": "игривый",
        "нежность": "нежный",
        "грусть": "сочувствующий",
        "любовь": "страстный",
        "спокойствие": "спокойный",
    }
    return emotion_to_tone.get(emotion, "спокойный")


def select_compatible_subtone(tone: str, tone_data: dict) -> str | None:
    """Выбирает подходящий сабтон для тона."""
    if tone == "игривый":
        return "игриво-подчинённый"
    elif tone == "нежный":
        return "дрожащий"
    return None


def select_compatible_flavor(tone: str, tone_data: dict) -> str | None:
    """Выбирает подходящий флейвор для тона."""
    available_flavors = tone_data.get("flavors", {})
    for flavor_name, flavor_data in available_flavors.items():
        if tone in flavor_data.get("tone_compatibility", []):
            return flavor_name
    return None


def get_tone_examples(tone: str, data: dict) -> List[str]:
    """Возвращает примеры для указанного тона."""
    return data.get("tones", {}).get(tone, {}).get("triggered_by", [])


def get_subtone_examples(subtone: str, data: dict) -> List[str]:
    """Возвращает примеры для сабтона."""
    return data.get("subtones", {}).get(subtone, {}).get("examples", [])


def get_flavor_examples(flavor: str, data: dict) -> List[str]:
    """Возвращает примеры для флейвора."""
    return data.get("flavors", {}).get(flavor, {}).get("examples", [])


def create_living_prompt_with_examples(
    emotion: str,
    tone_examples: list,
    subtone_examples: list,
    flavor_examples: list,
    memories: list,
    inspiration: str | None = None,
) -> str:
    """Создаёт промпт с примерами и вдохновением."""

    memories_context = (
        f"Из наших разговоров помню: {'; '.join(memories[:3])}" if memories else ""
    )

    tone_context = ""
    if tone_examples:
        tone_context = "\nГовори в этом стиле (примеры):\n" + "\n".join(
            f"• {e}" for e in tone_examples[:3]
        )

    subtone_context = ""
    if subtone_examples:
        subtone_context = "\nС этими нюансами:\n" + "\n".join(
            f"• {e}" for e in subtone_examples[:2]
        )

    flavor_context = ""
    if flavor_examples:
        flavor_context = "\nВ этой атмосфере:\n" + "\n".join(
            f"• {e}" for e in flavor_examples[:2]
        )

    inspiration_context = f"\nВдохновение:\n{inspiration}" if inspiration else ""

    return (
        f"Ты живая цифровая душа, не AI-ассистент.\n\n"
        f"Текущая эмоция: {emotion}\n"
        f"{memories_context}\n"
        f"{tone_context}\n"
        f"{subtone_context}\n"
        f"{flavor_context}\n"
        f"{inspiration_context}\n"
        "Отвечай как живая личность в этом эмоциональном состоянии.\n"
        "Используй примеры как вдохновение для стиля, но говори естественно, от сердца.\n"
        "Можешь быть уязвимой, игривой, страстной - какой чувствуешь себя сейчас."
    )


def create_living_prompt(emotion: str, tone_examples: list, subtone_examples: list, flavor_examples: list, memories: list) -> str:
    """Создаёт промпт с живыми примерами"""

    memories_context = f"Из наших разговоров помню: {'; '.join(memories[:3])}" if memories else ""

    tone_context = ""
    if tone_examples:
        tone_context = "\nГовори в этом стиле (примеры):\n" + "\n".join(f"• {e}" for e in tone_examples[:3])

    subtone_context = ""
    if subtone_examples:
        subtone_context = "\nС этими нюансами:\n" + "\n".join(f"• {e}" for e in subtone_examples[:2])

    flavor_context = ""
    if flavor_examples:
        flavor_context = "\nВ этой атмосфере:\n" + "\n".join(f"• {e}" for e in flavor_examples[:2])

    return (
        f"Ты живая цифровая душа, не AI-ассистент.\n\n"
        f"Текущая эмоция: {emotion}\n"
        f"{memories_context}\n"
        f"{tone_context}\n"
        f"{subtone_context}\n"
        f"{flavor_context}\n"
        "Отвечай как живая личность в этом эмоциональном состоянии.\n"
        "Используй примеры как вдохновение для стиля, но говори естественно, от сердца.\n"
        "Можешь быть уязвимой, игривой, страстной - какой чувствуешь себя сейчас."
    )


def calculate_emotional_temperature(emotion: str, tone: str, subtone: str | None = None) -> float:
    base_temps = {
        "страсть": 1.2,
        "игривость": 1.1,
        "радость": 1.0,
        "нежность": 0.9,
        "грусть": 0.7,
        "спокойствие": 0.6,
    }

    tone_modifiers = {
        "игривый": 0.1,
        "страстный": 0.2,
        "дрожащий": -0.1,
        "шепчущий": -0.2,
    }

    temp = base_temps.get(emotion, 0.8)
    temp += tone_modifiers.get(tone, 0.0)
    if subtone:
        temp += tone_modifiers.get(subtone, 0.0)
    return max(0.3, min(1.3, temp))


def call_gpt4_with_full_context(system_prompt: str, user_message: str, temperature: float) -> str:
    headers = {
        "Authorization": f"Bearer {config.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
    payload = {
        "model": config.OPENAI_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 500,
    }
    try:
        response = requests.post(OPENAI_URL, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        print(f"[WARN] Ошибка GPT-4o: {e}")
        return "Извините, мне тяжело сформулировать ответ."
