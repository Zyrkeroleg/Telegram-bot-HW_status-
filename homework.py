import os
import logging
import sys
from dotenv import load_dotenv
import requests
import time
import telegram
load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Бот отправляет сообщение."""
    try:
        bot.sendMessage(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.info('Сообщение отправленно')
    except telegram.TelegramError as error:
        logging.error(f'Ошибка при отправке сообщения {error}')


def get_api_answer(current_timestamp):
    """Проверяем ответ от API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(
            ENDPOINT,
            params=params,
            headers=HEADERS
        )
        if response.status_code != 200:
            logging.error('Сервер возвращает код, отличный от 200')
            raise
        return response.json()
    except requests.RequestException as error:
        logging.error(f'Ошибка отправки запроса. {error}')


def check_response(response):
    """Проверяем правильность запроса."""
    if not isinstance(response, dict):
        raise TypeError('Ответ API не словарь')
    if not response['homeworks'] and not response['current_date']:
        logging.error('В словаре нет необходимого ключа')
        raise Exception('В словаре нет необходимого ключа')
    homework = response['homeworks']
    if isinstance(homework, list):
        return homework
    raise Exception('Not list')


def parse_status(homework):
    """Получаем статус работы."""
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status in HOMEWORK_VERDICTS:
        verdict = HOMEWORK_VERDICTS.get(homework_status)
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    raise Exception('Wrong HW status')


def check_tokens():
    """Проверяем наличие переменных окружения."""
    if all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        return True
    logging.critical('отсутствует переменная окружения')
    return False


def main():
    """Основная логика работы бота."""
    if not check_tokens:
        raise KeyError('Отсутствует переменная окружения')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = 1
    last_response = ''
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            if homework != last_response and homework != []:
                last_response = homework
                message = parse_status(last_response[0])
                send_message(bot, message)
            current_timestamp = response.get('current_date')
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.critical(message)
            send_message(bot, message)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s- %(levelname)s - %(message)s',
        level=logging.INFO,
        handlers=[
            logging.FileHandler(
                'main.log',
                mode='w',
                encoding=None,
                delay=False
            ),
            logging.StreamHandler(sys.stdout)
        ],
    )
    main()
