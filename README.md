## Проект разработки бота в Телеграм 

### С чего начать?
Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Zyrkeroleg/api_final_yatube.git
```

Cоздать и активировать виртуальное окружение:
```
python3 -m venv venv
source venv/bin/activate
```
Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

#### Что делает?

Раз в 10 минут отправляет запрос на API сервиса Практикум.Домашка и проверяет статус отправленной на ревью домашней работы.

При обновлении статуса анализирует ответ API и отправлять соответствующее уведомление в Telegram.

Логирует свою работу и сообщает о важных проблемах сообщением в Telegram.

