from playwright.sync_api import sync_playwright
from loguru import logger
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

LOGIN = os.getenv('LOGIN')
PASSWORD = os.getenv('PASSWORD')
logger.info("Запуск браузера...")

with sync_playwright() as p:
    logger.add("file.log",
               format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
               rotation="3 days", backtrace=True, diagnose=True)

    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto("https://journal.top-academy.ru/")
    logger.info("Страница загружена")

    page.wait_for_selector('input[name="username"]', timeout=10000)

    page.fill('input[name="username"]', LOGIN)
    page.fill('input[name="password"]', PASSWORD)
    logger.info("Данные для входа введены")

    page.click('button[type="submit"]')
    logger.info("Кнопка входа нажата")

    page.wait_for_timeout(5000)

    logger.success(f"Вход выполнен! Текущий URL: {page.url}")

    page.goto("https://journal.top-academy.ru/main/homework/page/index")

    # Ждем загрузки страницы с домашними заданиями
    page.wait_for_selector('.homework-item', timeout=10000)
    logger.info("Страница с домашними заданиями загружена")

    # Ищем все элементы с домашними заданиями
    homework_items = page.query_selector_all('.homework-item')
    logger.info(f"Найдено элементов с домашними заданиями: {len(homework_items)}")

    # Проходим по каждому домашнему заданию
    for index, homework_item in enumerate(homework_items):
        try:
            # Проверяем, есть ли кнопка загрузки выполненного задания
            upload_button = homework_item.query_selector('.upload-file img[src*="upload.png"]')
            
            if upload_button:
                # Получаем информацию о предмете для логирования
                subject_element = homework_item.query_selector('.name-spec')
                subject_name = subject_element.inner_text() if subject_element else f"Задание {index + 1}"
                
                logger.info(f"Найдена кнопка загрузки для: {subject_name}")
                
                # Наводим курсор на элемент, чтобы показать кнопки
                homework_item.hover()
                page.wait_for_timeout(1000)  # Ждем появления кнопок
                
                # Кликаем на кнопку загрузки
                upload_button.click()
                logger.info(f"Клик на кнопку загрузки для: {subject_name}")
                
                # Ждем появления модального окна или формы загрузки
                page.wait_for_timeout(3000)
                
                # Здесь можно добавить логику для загрузки файла
                # Например: page.set_input_files('input[type="file"]', 'путь/к/файлу')
                
                logger.success(f"Готово к загрузке файла для: {subject_name}")
                
        except Exception as e:
            logger.error(f"Ошибка при обработке задания {index + 1}: {e}")

    logger.info("Обработка домашних заданий завершена")

    input("Вход выполнен. Нажмите Enter для закрытия...")

    browser.close()