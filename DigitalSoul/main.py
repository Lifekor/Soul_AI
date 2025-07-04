"""Консольный интерфейс для Digital Soul."""

from .soul_core import SoulCore


def main():
    print("=== Цифровая душа пробуждается ===")
    soul = SoulCore()
    while True:
        try:
            user_message = input("Пользователь: ")
        except (KeyboardInterrupt, EOFError):
            print()  # перенос строки
            break
        if user_message.lower() in {"exit", "выход"}:
            break
        response = soul.process_message(user_message)
        print(f"Душа: {response}")


if __name__ == "__main__":
    main()
