# Audio Service

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue)

**Audio Service** — это REST API на базе FastAPI для управления пользователями и загрузки аудиофайлов. Приложение поддерживает авторизацию через Яндекс OAuth, хранение данных в PostgreSQL и контейнеризацию через Docker.

## Возможности
- Регистрация и авторизация пользователей через Яндекс OAuth.
- Обновление данных пользователей (email, статус суперюзера).
- Загрузка и управление аудиофайлами (в разработке).
- Асинхронная работа с базой данных через SQLAlchemy и asyncpg.
- Деплой через Docker и Docker Compose.

---

## Требования
- Python 3.11+
- Docker и Docker Compose (для контейнеризации)
- PostgreSQL 16 (если запускаете без Docker)

---

## Структура проекта
```text
Audio_Service/
├── Dockerfile          # Конфигурация Docker-образа
├── docker-compose.yml  # Конфигурация Docker Compose
├── requirements.txt    # Зависимости Python
├── uploads/            # Папка для загруженных файлов
└── app/
    ├── main.py         # Точка входа FastAPI
    ├── routes/         # Эндпоинты API
    ├── database/       # Работа базы данных и репозитории
    ├── services/       # Бизнес-логика
    ├── schemas/        # Pydantic-схемы
    └── models/         # SQLAlchemy-модели
```

## Установка

### Docker установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/UnwreckerNick/audio_service.git
   cd audio_service
   ```
2. Убедитесь, что Docker и Docker Compose установлены:
   ```bash
   docker --version
   docker-compose --version
   ```
3. Настройте .env для Postgres, Яндекс OAuth и JWT:
   ```bash
   DATABASE_URL=your_db_url
   SYSTEM_DATABASE_URL=your_system_db_url
   ALGORYTHM=your_algorythm
   YANDEX_CLIENT_ID=your_yandex_client_id
   YANDEX_CLIENT_SECRET=your_yandex_client_secret
   ```
4. Создайте папку для загрузок:
   ```bash
   mkdir -p uploads
   ```
5. Соберите и запустите контейнеры:
   ```bash
   docker-compose up --build
   ```

## Использование API
API доступно по адресу `http://127.0.0.1:8000`. Интерактивная документация: `/docs`.

### Основные эндпоинты
1. Авторизация через Яндекс:

* GET /users/login/yandex — перенаправляет на Яндекс OAuth.
* После авторизации возвращает токен через /users/auth/yandex/callback.
  Пример ответа:
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "token_type": "bearer"
   }
   ```
2. Обновление пользователя:
   ```bash
   curl -X PUT "http://127.0.0.1:8000/users/1" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <your_token>" \
     -d '{"email": "newemail@example.com"}'
   ```
3. Загрузка аудиофайла:
   ```bash
   curl -X POST "http://127.0.0.1:8000/audio/upload?name=test_audio" \
     -H "Authorization: Bearer <your_token>" \
     -F "file=@/path/to/audiofile.mp3"
   ```
