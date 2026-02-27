import os
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class BotConfig:
    # ... предыдущие переменные ...
    
    # Webhook
    USE_WEBHOOK: bool = os.getenv("USE_WEBHOOK", "false").lower() == "true"
    WEBHOOK_PATH: str = os.getenv("WEBHOOK_PATH", "/webhook")
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")  # ваш домен + путь
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "")
    WEBHOOK_HOST: str = os.getenv("WEBHOOK_HOST", "0.0.0.0")
    WEBHOOK_PORT: int = int(os.getenv("WEBHOOK_PORT", 8443))
    
    # Sentry
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    
    # ML модель
    ML_MODEL_PATH: str = os.getenv("ML_MODEL_PATH", "models/risk_model.pkl")
    ML_FEATURES: List[str] = os.getenv("ML_FEATURES", "tx_count,avg_amount,unique_contracts,origin_risk").split(",")
    
    # Кэширование в БД
    CACHE_TTL_DAYS: int = int(os.getenv("CACHE_TTL_DAYS", 7))
    
    # Blacklist обновление
    BLACKLIST_UPDATE_INTERVAL: int = int(os.getenv("BLACKLIST_UPDATE_INTERVAL", 86400))  # 24 часа
    BLACKLIST_SOURCES: List[str] = os.getenv("BLACKLIST_SOURCES", "https://api.cryptoscamdb.org/v1/addresses").split(",")
