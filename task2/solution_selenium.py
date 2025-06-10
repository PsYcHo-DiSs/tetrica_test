import time
import pandas as pd
from collections import defaultdict
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def setup_driver():
    """Создаёт и настраивает headless Selenium-драйвер."""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def get_beast_counts():
    """Собирает количество животных по алфавиту с Википедии."""
    url = 'https://ru.wikipedia.org/wiki/Категория:Животные_по_алфавиту'
    counts = defaultdict(int)

    with setup_driver() as driver:
        driver.get(url)
        time.sleep(1)

        pbar = tqdm(desc="Обработка страниц", unit="стр.")
        while True:
            items = driver.find_elements(By.CSS_SELECTOR, '#mw-pages li a')
            for item in items:
                name = item.text.strip()
                if name:
                    letter = name[0].upper()
                    counts[letter] += 1

            next_buttons = driver.find_elements(By.LINK_TEXT, 'Следующая страница')
            if next_buttons:
                next_buttons[0].click()
                time.sleep(0.5)
                pbar.update(1)
            else:
                break
        pbar.close()

    return counts


def save_to_csv(counts: dict, filename='beasts.csv'):
    """Сохраняет результат в файл CSV с сортировкой по буквам."""
    df = pd.DataFrame(sorted(counts.items()), columns=['Буква', 'Количество'])
    df.to_csv(filename, index=False, encoding='utf-8-sig')


if __name__ == '__main__':
    beast_counts = get_beast_counts()
    save_to_csv(beast_counts)
    print('✅ Готово! Результат сохранён в файле beasts.csv')
