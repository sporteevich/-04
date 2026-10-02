# Практическая работа №5 — «Автосалон»

Django + DRF (JWT) API из 5 модулей и Streamlit-дашборд.

## Модули

| Модуль | Приложение | Назначение | Базовый URL |
|---|---|---|---|
| 1 | `apps/accounts` | Авторизация, кастомный `User` с должностью | `/api/auth/` |
| 2 | `apps/catalog` | Марки и автомобили | `/api/brands/`, `/api/cars/` |
| 3 | `apps/clients` | Клиенты салона | `/api/clients/` |
| 4 | `apps/orders` | Заказы (покупка / тест-драйв / сервис) | `/api/orders/` |
| 5 | `apps/reports` | Аналитика и KPI | `/api/reports/` |

## Эндпоинты

**Модуль 1 — авторизация**
- `POST /api/auth/register/` — регистрация, сразу выдаёт пару токенов
- `POST /api/auth/login/` — вход, выдаёт `access` + `refresh`
- `GET  /api/auth/me/` — текущий пользователь
- `POST /api/auth/token/refresh/` — обновление access-токена

**Модули 2–4 — CRUD через ViewSet**
- `GET|POST /api/cars/`, `GET|PUT|DELETE /api/cars/{id}/`
  фильтры: `?brand=1&status=available&fuel_type=petrol&year=2024`,
  поиск `?search=camry`, сортировка `?ordering=-price`
- `GET|POST /api/brands/`, `GET|POST /api/clients/`, `GET|POST /api/orders/`
- `POST /api/orders/{id}/complete/` — завершить заказ (авто → «Продан»)
- `POST /api/orders/{id}/cancel/` — отменить заказ (авто → «В наличии»)

**Модуль 5 — отчёты**
- `GET /api/reports/kpi/?days=30`
- `GET /api/reports/revenue/?days=30`
- `GET /api/reports/top-models/?limit=5`
- `GET /api/reports/manager-load/?days=30`
- `GET /api/reports/stock/`

## Каскадная логика заказов

- создание заказа типа «Покупка» → авто переходит `available → reserved`;
- `complete()` → `reserved → sold`, проставляется `completed_at`;
- `cancel()` → `reserved → available`.

## Запуск

```powershell
# 1. Виртуальное окружение
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. База данных (в psql под суперпользователем)
#   CREATE USER autosalon WITH PASSWORD 'autosalon_pass';
#   CREATE DATABASE autosalon_db OWNER autosalon;
#   GRANT ALL PRIVILEGES ON DATABASE autosalon_db TO autosalon;

# 3. Миграции и суперпользователь
python manage.py makemigrations accounts catalog clients orders
python manage.py migrate
python manage.py createsuperuser

# 4. API
python manage.py runserver

# 5. Дашборд (во втором терминале, окружение активировано)
streamlit run dashboard/app.py
```

- Админка: http://localhost:8000/admin/
- DRF-браузер: http://localhost:8000/api/cars/ (вход через `/api/drf-login/`)
- Дашборд: http://localhost:8501 — логин/пароль те же, что у пользователя Django.

## Проверка API через PowerShell

```powershell
$r = Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/auth/login/ `
     -ContentType "application/json" `
     -Body '{"username":"admin","password":"admin"}'
$h = @{ Authorization = "Bearer $($r.access)" }
Invoke-RestMethod -Uri http://localhost:8000/api/reports/kpi/?days=30 -Headers $h
```

## Настройки

Параметры БД и ключ берутся из `.env` (см. `.env.example`):
`SECRET_KEY`, `DEBUG`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `API_URL`.

Аутентификация — JWT (`access` 8 часов, `refresh` 7 дней), доступ к API по умолчанию
только для авторизованных (`IsAuthenticated`), пагинация по 20 записей, CORS открыт для разработки.
