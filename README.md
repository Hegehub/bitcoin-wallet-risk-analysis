```markdown
# 🔍 RiskAnalyzer Bot – профессиональный анализ рисков крипто-кошельков

Telegram-бот для анализа рисков BTC и ETH адресов. Определяет происхождение средств, вычисляет процент риска, поддерживает подписки с оплатой в Bitcoin, двухфакторную аутентификацию и предоставляет полную админ-панель.

---

## 🚀 Возможности

- **Анализ рисков** BTC/ETH адресов (0–100%)
- **Категоризация происхождения средств** – биржа, майнинг, DeFi, NFT, гемблинг, миксеры, даркнет, неизвестно
- **Система подписок**:
  - Бесплатный – 3 анализа в день
  - PRO – 0.001 BTC/месяц (безлимит, расширенный отчёт)
  - Business – 0.005 BTC/месяц (API, white‑label, приоритет)
- **Оплата в Bitcoin** через WalletPay (QR-код, ссылка)
- **Двухфакторная аутентификация (2FA)** на основе TOTP (Google Authenticator) – обязательна для администраторов, опциональна для пользователей
- **Защита от атак** – WAF (SQLi, XSS, command injection), rate limiting, автоматическая блокировка
- **Админ-панель** в Telegram – статистика, управление пользователями, экспорт данных, безопасность
- **Кэширование в Redis** – ускорение повторных запросов
- **Асинхронная архитектура** – высокая производительность
- **Docker-контейнеризация** – лёгкое развёртывание
- **Мониторинг** – Prometheus метрики + Grafana дашборды

---

## 🛠️ Технологии

- Python 3.11, [aiogram 3.x](https://docs.aiogram.dev/)
- PostgreSQL, SQLAlchemy (asyncpg)
- Redis (кэш, FSM, очереди)
- Docker, docker-compose
- Bitcoin API (blockchain.info), Ethereum (Infura, Etherscan)
- [WalletPay](https://pay.wallet.tg) – приём Bitcoin платежей
- 2FA: pyotp + qrcode
- Безопасность: WAF, rate limiting, шифрование секретов
- Мониторинг: Prometheus, Grafana

---

## 📦 Быстрый старт (Docker)

### 1. Клонируйте репозиторий
```bash
git clone https://github.com/yourusername/risk-analyzer-bot.git
cd risk-analyzer-bot
```

2. Настройте переменные окружения

Скопируйте .env.example в .env и заполните свои ключи:

```bash
cp .env.example .env
nano .env
```

3. Запустите все сервисы

```bash
docker-compose up -d --build
```

4. Просмотрите логи

```bash
docker-compose logs -f bot
```

5. Откройте Telegram

Напишите вашему боту команду /start – вы увидите приветствие.

---

⚙️ Ручная установка (без Docker)

Предварительные требования

· Python 3.11+
· PostgreSQL (>=13)
· Redis (>=6)

1. Создайте виртуальное окружение и установите зависимости

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
# venv\Scripts\activate    # Windows

pip install -r requirements.txt
```

2. Настройте базу данных

Создайте базу данных PostgreSQL:

```sql
CREATE DATABASE riskbot;
```

3. Заполните .env

Скопируйте .env.example в .env и укажите:

· BOT_TOKEN
· ADMIN_IDS (ваши Telegram ID)
· DATABASE_URL (например postgresql://user:pass@localhost/riskbot)
· REDIS_URL (например redis://localhost:6379/0)
· Ключи для Etherscan/Infura, WalletPay и т.д.

4. Примените миграции (если используются)

```bash
alembic upgrade head
```

5. Запустите бота

```bash
python main.py
```

---

🔐 Конфигурация (.env)

Обязательные переменные:

Переменная Описание
BOT_TOKEN Токен Telegram бота (от @BotFather)
ADMIN_IDS ID администраторов через запятую
DATABASE_URL Строка подключения к PostgreSQL
REDIS_URL Строка подключения к Redis
ENCRYPTION_KEY 32-символьный ключ для шифрования 2FA
WALLETPAY_API_KEY API ключ от WalletPay
WALLETPAY_STORE_ID Store ID из WalletPay

Необязательные, но рекомендуемые:

· ETHERSCAN_API_KEY, INFURA_API_KEY – для Ethereum анализа
· ABUSEIPDB_API_KEY, IPINFO_TOKEN – для проверки IP (безопасность)
· PRO_PRICE_BTC, BUSINESS_PRICE_BTC – цены подписок в BTC

Полный список см. в .env.example.

---

📚 Команды бота

Для всех пользователей

Команда Описание
/start Приветствие и главное меню
/help Справка
/analyze <адрес> Анализ крипто-кошелька (BTC или ETH)
/subscription Информация о подписках и покупка
/setup_2fa Настройка двухфакторной аутентификации
/disable_2fa <код> Отключение 2FA с подтверждением
/backup_codes <код> Получение новых резервных кодов
/my_stats Статистика использования (количество анализов)
/feedback Отправить отзыв разработчикам

Для администраторов

Команда Описание
/admin Панель администратора
/userinfo <id> Детальная информация о пользователе
/alert <текст> Массовая рассылка сообщения всем пользователям
/export <users/payments/analyses> Экспорт данных в Excel
/stats Краткая статистика системы
/security Просмотр дашборда безопасности
/broadcast <текст> Отправить сообщение в ЛС всем пользователям

---

🔒 Безопасность

· 2FA – обязательна для администраторов, настраивается через /setup_2fa.
· WAF Middleware – блокирует SQL-инъекции, XSS, command injection и path traversal.
· Rate Limiting – не более 100 запросов в минуту с одного пользователя.
· Автоматическая блокировка – после 5 нарушений пользователь блокируется на 24 часа.
· Шифрование секретов – ключи 2FA хранятся в БД в зашифрованном виде.
· Подпись запросов – опционально для API (HMAC-SHA256).

---

📊 Мониторинг

· Prometheus – метрики доступны на порту 8000 (путь /metrics):
  · analysis_requests_total – количество анализов
  · analysis_duration_seconds – гистограмма времени анализа
  · cache_hits_total, cache_misses_total – эффективность кэша
  · active_users – активные пользователи за последние 24 часа
  · subscription_tiers – распределение подписок
· Grafana – готовые дашборды находятся в папке grafana/. Импортируйте их в свою Grafana.
· Логи – пишутся в logs/bot.log и в stdout (docker logs).

---

📝 Лицензия

Этот проект распространяется под лицензией MIT. Подробнее см. файл LICENSE.

---

🤝 Контакты и поддержка

· Telegram: @hegehub
· GitHub Issues: создать issue

Если вам понравился проект, поставьте ⭐ на GitHub!

```
