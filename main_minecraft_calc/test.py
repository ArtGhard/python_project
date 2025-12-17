import requests


def get_number_fact(n):
    try:
        # Используем HTTPS и таймаут
        response = requests.get(f"https://numbersapi.com/{n}", timeout=5)
        if response.status_code == 200:
            return response.text
        else:
            return "Факт не найден."
    except requests.exceptions.RequestException as e:
        return f"Ошибка: {type(e).__name__}"


print(get_number_fact(42))
