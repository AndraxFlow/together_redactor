# together_redactor

## Локально (без Docker)

1. Установка зависимостей:
`pip install -r requirements.txt`

2. Создай `.env` на основе `.env.example` и проверь параметры БД.

3. Применить миграции:
`alembic upgrade head`

4. Запустить API:
`uvicorn app.main:app --reload`

5. Swagger:
`http://127.0.0.1:8000/docs`

## Запуск через Docker

1. Поднять контейнеры:
`docker compose up --build`

2. Если нужно применить миграции отдельно:
`docker compose exec app alembic upgrade head`

3. Остановить:
`docker compose down`

## Makefile (основные команды)

Показать список команд:
`make help`

Частые команды:
- `make up` - поднять контейнеры
- `make down` - остановить контейнеры
- `make logs` - смотреть логи
- `make migrate` - применить `alembic upgrade head`

Как проверить, что миграция реально применилась:
- `make current` - текущая ревизия Alembic (например, `0001_initial_schema (head)`)
- `make version` - содержимое таблицы `alembic_version`
- `make table-status` - список таблиц в БД (`\dt`)

## Auth endpoints

- `POST /auth/register` - регистрация пользователя
- `POST /auth/login` - логин и получение JWT
- `GET /auth/me` - защищенный endpoint с `Authorization: Bearer <token>`

Для WebSocket токен передается как query-параметр:
`ws://localhost/ws/<document_id>?token=<JWT>`

routers - ручки
models - модели ORM 
db - Подключение к ДБ
core - конфигурации
crdt - работа с Y-py
services - бизнес-логика
schemas - схемы работы 
websocket - логика работы websocket`a