import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import pandas as pd
import time
from urllib3.exceptions import SSLError
from requests.exceptions import RequestException

BASE_URL = "https://ru.wikipedia.org"
CATEGORY_URL = f"{BASE_URL}/wiki/Категория:Животные_по_алфавиту"
OUTPUT_CSV = "beasts_bs4_.csv"


def fetch_html(url, retries=3, delay=1.0):
    """Получает HTML-страницу с заданного URL с обработкой ошибок и повторными попытками."""
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except (SSLError, RequestException) as e:
            print(f"[{attempt}/{retries}] Ошибка при загрузке {url}:\n{e}")
            if attempt < retries:
                time.sleep(delay)
            else:
                raise


def parse_animals_from_page(html):
    """
    Извлекает имена животных с текущей страницы и считает количество по первой букве.
    Возвращает (словарь {буква: количество}, ссылка на следующую страницу или None).
    """
    soup = BeautifulSoup(html, 'html.parser')
    counts = defaultdict(int)

    for link in soup.select('#mw-pages li a'):
        name = link.text.strip()
        if name:
            first_letter = name[0].upper()
            counts[first_letter] += 1

    next_link = soup.select_one('#mw-pages a:-soup-contains("Следующая страница")')
    next_url = BASE_URL + next_link['href'] if next_link else None

    return counts, next_url


def collect_all_counts(start_url):
    """Проходит по всем страницам категории и собирает статистику."""
    total_counts = defaultdict(int)
    current_url = start_url
    page_counter = 0

    while current_url:
        page_counter += 1
        print(f"→ Обработка страницы {page_counter}: {current_url}")
        try:
            html = fetch_html(current_url)
            page_counts, current_url = parse_animals_from_page(html)
            for letter, count in page_counts.items():
                total_counts[letter] += count
        except Exception as e:
            print(f"❌ Ошибка на странице {current_url}: {e}")
            break

        if page_counter % 10 == 0:
            print(f"✓ Пройдено {page_counter} страниц")

        time.sleep(0.1)

    return total_counts


def save_counts_to_csv(counts, filename):
    """Сохраняет результат в CSV."""
    df = pd.DataFrame(sorted(counts.items()), columns=['Буква', 'Количество'])
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"📁 Данные сохранены в {filename}")


if __name__ == '__main__':
    print("🚀 Начинаем сбор данных...")
    final_counts = collect_all_counts(CATEGORY_URL)
    save_counts_to_csv(final_counts, OUTPUT_CSV)
    print("✅ Готово!")
