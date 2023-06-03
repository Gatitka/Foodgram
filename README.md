# praktikum_new_diplom

внести данные ингридиентов
```
python manage.py load_ingridients_data
```

для запуска реакта в папке фронтэнда запустить из терминала
```
npm run start
```
для установки psycopg2 в контейнерах добавить в бокерфайл бэкэнда инструкцию, но можно и без него, установив лишь psycopg2-binary:
```
RUN apt-get install libpq-dev python-dev
```
