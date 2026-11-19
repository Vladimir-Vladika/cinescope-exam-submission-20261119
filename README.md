# CineScope — API autotests

Отдельный проект для экзамена Coconut School. Python 3.12+, pytest, requests,
Faker. Тесты выполняются против реального учебного стенда CineScope.

## Статус

Реализованы 32 тестовых случая для Movies API. Результат фактического прогона
и ограничения проверки указаны в `VALIDATION.md`. Наличие кода не означает,
что весь набор уже прошёл на стенде.

## Быстрый запуск в Windows / PyCharm

Скачайте ветку `exam` или клонируйте её:

```powershell
git clone -b exam https://github.com/Vladimir-Vladika/cinescope-exam-submission-20261119.git
cd cinescope-exam-submission-20261119
```

Откройте **эту новую папку** как отдельный проект. В терминале из корня:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

В `.env` укажите `ADMIN_EMAIL` и `ADMIN_PASSWORD` тестовой учётной записи
с ролью `SUPER_ADMIN`. Альтернатива — действующий `ADMIN_TOKEN` этой роли.
Пароли и токены не добавляются в Git. Обычная регистрация даёт роль `USER`
и не обеспечивает права на создание/изменение/удаление фильмов.

```powershell
# Полный экзаменационный набор (требует SUPER_ADMIN)
.\.venv\Scripts\python.exe -m pytest

# Только доступные без административной учётной записи проверки
.\.venv\Scripts\python.exe -m pytest -m public

# Основные положительные сценарии
.\.venv\Scripts\python.exe -m pytest -m smoke

# Отчёт JUnit
.\.venv\Scripts\python.exe -m pytest --junitxml=reports/results.xml
```

В Linux/macOS аналогично: `python3 -m venv .venv`, затем используйте
`.venv/bin/python` вместо `.\.venv\Scripts\python.exe`.

## Структура и связи

| Файл | Ответственность |
| --- | --- |
| `config/settings.py` | Адреса сервисов, тайм-аут, секреты из окружения / `.env` |
| `custom_requester/custom_requester.py` | HTTP-запрос, безопасный лог, проверка статуса, возврат `Response` |
| `clients/movies_api.py` | Все пять операций с фильмами |
| `clients/auth_api.py` | Логин и получение ответа с accessToken |
| `clients/genres_api.py` | Получение актуальных жанров для данных |
| `clients/api_manager.py` | Объединение клиентов для одной Session |
| `utils/data_generator.py` | Faker и уникальные названия, переопределение полей |
| `tests/conftest.py` | Сессии, авторизация, данные, создание и удаление своих фильмов |
| `tests/api/test_movies_public.py` | Список, некорректные фильтры, создание без авторизации |
| `tests/api/test_movies_crud.py` | Создание, чтение, PATCH, удаление, ошибки и проверка сохранения |
| `tests/api/test_movies_filters.py` | Диапазон цен, обе границы, равные границы, включение и исключение своих фильмов |

Тест получает `ApiManager` из фикстуры, вызывает `MoviesAPI`; клиент вызывает
`CustomRequester`, а тот — `requests.Session.request`. Ответ возвращается в тест.
`DataGenerator` только создаёт словарь и не отправляет запросы.

## Независимость и очистка

- У каждого теста отдельная Session; публичный клиент не получает токен администратора.
- Названия используют UUID. ID фильмов берутся из ответов, ID жанра — из API.
- `created_movie` создаёт фильм через `tracked_create`. Фикстура `tracked_create`
  удаляет все зарегистрированные фильмы в teardown, даже при падении assert в тесте.
- Неожиданно успешное создание в негативном тесте тоже регистрируется для удаления.
- Повторное удаление при cleanup допускает 404: фильм уже мог удалить сам тест.
  В самих тестах ожидаемые статусы проверяются строго.
- Проверки 404 используют ID собственного удалённого фильма. Чужие фильмы не меняются.
- Ошибки очистки видны как ошибки teardown. Если сеть оборвалась после создания,
  но до получения ID, автоматическое удаление невозможно: ищите имя `AQA-…` на стенде.
- Фильтры проверяют не только значения в ответе, но и наличие своих подходящих
  фильмов, отсутствие неподходящих и все страницы выдачи. Пустой список не даёт
  ложноположительного результата.
- Нет автоматических повторов POST/PATCH/DELETE и нет пропуска проверок при
  отсутствии учётной записи: полный прогон честно сообщает ошибку конфигурации.

## Требования и документация

По восстановленному перечню экзамена реализованы CustomRequester, ApiManager,
DataGenerator, Movies API, позитивные/негативные тесты, фильтрация, фикстура
создания фильма, независимые данные, `.gitignore` и `requirements.txt`.
Полное соответствие исходной странице экзамена нужно сверить после восстановления
доступа к школе: в момент подготовки она не открывалась.

- Экзамен: https://www.coconutschool.ru/courses/2/modules/45/lessons/506
- Movies: https://api.dev-cinescope.coconutqa.ru/swagger
- Auth: https://auth.dev-cinescope.coconutqa.ru/swagger

Восстановленное требование к сдаче — ссылка на Pull Request из ветки `exam`
в `main`. В архиве есть Git bundle с этими ветками и инструкция публикации.
