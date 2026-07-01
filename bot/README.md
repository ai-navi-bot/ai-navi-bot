# AI NAVI Bot

Telegram-бот на Python с использованием [aiogram 3.x](https://docs.aiogram.dev/).

## Структура проекта

```
bot/
├── app.py              # Точка входа
├── config.py           # Конфигурация и переменные окружения
├── handlers.py         # Обработчики команд и сообщений
├── states.py           # FSM-состояния
├── questions.py        # Вопросы опроса
├── excel.py            # Работа с Excel
├── keyboards.py        # Клавиатуры
├── requirements.txt    # Зависимости
├── .env.example        # Пример файла окружения
├── README.md
└── data/
    └── responses.xlsx  # Файл для сохранения ответов
```

## Требования

- Python 3.10 или новее
- Аккаунт Telegram и токен бота от [@BotFather](https://t.me/BotFather)

## Установка

### 1. Клонирование и переход в каталог проекта

```bash
cd bot
```

### 2. Создание виртуального окружения

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (cmd):**

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

После активации в начале строки терминала появится префикс `(venv)`.

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Создание файла `.env`

Скопируйте пример конфигурации:

**Windows (PowerShell):**

```powershell
Copy-Item .env.example .env
```

**Linux / macOS:**

```bash
cp .env.example .env
```

Откройте `.env` и замените значение `YOUR_BOT_TOKEN` на реальный токен бота.

## Как получить Telegram Token

1. Откройте Telegram и найдите [@BotFather](https://t.me/BotFather).
2. Отправьте команду `/newbot`.
3. Введите имя бота (отображаемое имя).
4. Введите username бота (должен заканчиваться на `bot`, например `ai_navi_bot`).
5. BotFather пришлёт сообщение с токеном вида:

   ```
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

6. Скопируйте токен и вставьте в файл `.env`:

   ```
   BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

> **Важно:** не публикуйте токен в репозитории и не передавайте его третьим лицам.

## Запуск бота

Убедитесь, что виртуальное окружение активировано и файл `.env` настроен.

```bash
python app.py
```

При успешном запуске в консоли появится:

```
========================
AI NAVI Bot started
========================
```

Откройте своего бота в Telegram и отправьте команду `/start`. Бот ответит:

```
Бот успешно запущен.
```

## Остановка бота

Нажмите `Ctrl+C` в терминале, где запущен бот.

## Возможные ошибки

| Ошибка | Решение |
|--------|---------|
| `BOT_TOKEN не задана` | Создайте `.env` и укажите `BOT_TOKEN` |
| `ModuleNotFoundError` | Активируйте venv и выполните `pip install -r requirements.txt` |
| Бот не отвечает | Проверьте токен и интернет-соединение |

## Дальнейшая разработка

- `handlers.py` — новые команды и обработчики сообщений
- `states.py` — FSM-состояния для пошаговых сценариев
- `questions.py` — тексты и логика вопросов
- `excel.py` — сохранение ответов в `data/responses.xlsx`
- `keyboards.py` — клавиатуры для пользователя
