# Foodgram:

## Ресурс с рецептами любимых блюд.:memo:
[перейти на сайт](http://51.250.10.113/)


Проект Foodgram собирает рецепты пользователей.
С использованием Continuous Integration и Continuous Deployment настроен workflow GitHub Actions таким образом. При пуше в ветку main автоматически отрабатывают сценарии:

- Автоматический запуск тестов,
- Обновление образов на Docker Hub,
- Автоматический деплой на боевой сервер,
- Отправка сообщения в телеграмм-бот в случае успеха.

##### Все инструкции описаны в:
```
.github\workflows\blank.yml
```

## Начало работы
Клонируйте репозиторий на локальную машину.
```
git clone <адрес репозитория>
```
Для работы с проектом локально - установите вирутальное окружение и восстановите зависимости.
```
python -m venv venv
pip install -r requirements.txt
```
### Подготовка удаленного сервера для развертывания приложения
Для работы с проектом на удаленном сервере должен быть установлен Docker и docker-compose. Эта команда скачает скрипт для установки докера:
```
curl -fsSL https://get.docker.com -o get-docker.sh
```
Эта команда запустит его:
```
sh get-docker.sh
```
Установка docker-compose:
```
apt install docker-compose
```
Создайте папки foodgram/infra/ на удаленном сервере. В папку infra/ и скопируйте файлы docker-compose.yaml, nginx.conf (из папки infra). В общую папку foodgram/ скопируйте папки data/, docs/.
Команда для копирования файлов на сервер(находясь в папке с копируемым документом):
```
scp <FILENAME> <USER>@<HOST>:/home/<USER>/yamdb_final/
```
### Подготовка репозитория на GitHub
Для использования Continuous Integration и Continuous Deployment необходимо в репозитории на GitHub прописать Secrets - переменные доступа к вашим сервисам. Переменые прописаны в workflows/blank.yaml
- DB_ENGINE, DB_HOST, DB_NAME, DB_PORT, HOST, POSTGRES_USER, POSTGRES_PASSWORD - для подключения к базе данных
- PASSWORD_DOCKERHUB, USERNAME_DOCKERHUB - для загрузки и скачивания образа с DockerHub
- USER, HOST, PASSPHRASE, SSH_KEY, SECRET_KEY - для подключения к удаленному серверу
- TELEGRAM_TO, TELEGRAM_TOKEN - для отправки сообщений в Telegram

### Развертывание приложения
При пуше в ветку main приложение пройдет тесты, обновит образ на DockerHub и сделает деплой на сервер. Дальше необходимо подлкючиться к серверу.
```
ssh <USER>@<HOST>
```
Перейдите в запущенный контейнер приложения командой:
```
docker container exec -it <CONTAINER ID> bash
```
Внутри контейнера необходимо выполнить миграции и собрать статику приложения:
```
python manage.py collectstatic --no-input
python manage.py migrate
```
Для использования панели администратора по адресу http://0.0.0.0/admin/ необходимо создать суперпользователя.
```
python manage.py createsuperuser
```
Для загрузки ингредиентов из папки data/ в базу используется следующая команда.
```
python manage.py load_ingridients_data
```
К проекту по адресу http://0.0.0.0/redoc/ подключена документация API. В ней описаны шаблоны запросов к API и ответы. Для каждого запроса указаны уровни прав доступа - пользовательские роли, которым разрешён запрос.
## Технологии используемые в проекте
Python, Django, Django REST Framework, PostgreSQL, Nginx, Docker, GitHub Actions

## Авторы
Natalia Kirilova - автор, студентка курса Python-разработчик в Яндекс.Практикум. Это учебный проект. Если есть вопросы или пожелания по проекту пишите на почту - gatitka@yandex.ru
