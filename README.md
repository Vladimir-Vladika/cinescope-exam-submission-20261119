# CineScope — API autotests

Отдельный проект для экзамена Coconut School. Python 3.12+, pytest, requests,
Faker. Тесты выполняются против реального учебного стенда CineScope.

## Статус

Реализованы и проверены на реальном стенде все 32 тестовых случая для Movies API:
**32 passed in 256.84s**, без пропусков и ошибок (19 ноября 2026).
Из них 21 тест требует SUPER_ADMIN, 11 доступны без административных прав.
Подробности прогона и ограничения среды указаны в `VALIDATION.md`.

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
| `tests/api/test_movies_public.py` | Список, некорректные фильтры, равные границы цен, создание без авторизации |
| `tests/api/test_movies_crud.py` | Создание, чтение, PATCH, удаление, ошибки и проверка сохранения |
| `tests/api/test_movies_filters.py` | Диапазон цен, обе границы, включение и исключение своих фильмов |

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

Описание экзамена прочитано и сверено с кодом 19 ноября 2026.

| Требование экзамена | Реализация / статус |
| --- | --- |
| API-класс Movies и методы из документации | `MoviesAPI`: GET списка, POST, GET по ID, PATCH, DELETE |
| CustomRequester, ApiManager, DataGenerator | Реализованы в отдельных модулях |
| Позитивные и негативные тесты | `tests/api/test_movies_public.py`, `test_movies_crud.py` |
| Минимум один тест фильтра GET /movies | Диапазон с проверкой границ в `test_movies_filters.py`; равные границы отклоняются в `test_movies_public.py` |
| Фикстура создания фильма | `created_movie`, очистка через `tracked_create` |
| Генерация данных и независимость | Faker, UUID, отдельные Session, собственные фильмы |
| .gitignore и requirements.txt | В корне репозитория |
| Отдельная ветка и Pull Request | Ветка `exam`, PR №1 в `main` |
| Все тесты проходят, стабильность и повторяемость | Полный прогон: 32 passed, без skip/xfail; фикстуры очищают свои данные |

Сценарии сгруппированы по проверяемому поведению. Числовые значения в проверках
границ и некорректные значения — намеренные тестовые условия; ID фильмов и жанров
не зашиты в код. Полный прогон успешно выполнен на реальном учебном стенде.

- Экзамен: https://www.coconutschool.ru/courses/2/modules/45/lessons/506
- Movies: https://api.dev-cinescope.coconutqa.ru/swagger
- Auth: https://auth.dev-cinescope.coconutqa.ru/swagger

Сдача: отправить ссылку на Pull Request через раздел «Практика» урока «Экзамен»:
https://github.com/Vladimir-Vladika/cinescope-exam-submission-20261119/pull/1

В инструкции школы базовая ветка названа `master`; здесь используется `main`.
Код экзамена находится в отдельной ветке `exam`, PR открыт и не слит.
