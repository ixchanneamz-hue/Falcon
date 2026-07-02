import os

TOKEN = os.getenv("TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "986072050"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "-1003987665896"))
BOT_USERNAME = os.getenv("BOT_USERNAME", "IxchanneBot")
BINANCE_WALLET = os.getenv("BINANCE_WALLET", "")
NETWORK = os.getenv("NETWORK", "TRC20")
CURRENCY = os.getenv("CURRENCY", "USDT")
MIN_WITHDRAW = float(os.getenv("MIN_WITHDRAW", "1.0"))
DATABASE_URL = os.getenv("DATABASE_URL", "")
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://t.me/gooodertg")
REFERRAL_REGISTRATION_BONUS = float(os.getenv("REFERRAL_REGISTRATION_BONUS", "0.05"))
REFERRAL_COMMISSION_RATE = float(os.getenv("REFERRAL_COMMISSION_RATE", "0.10"))
CAMPAIGN_REWARD = float(os.getenv("CAMPAIGN_REWARD", "0.005"))


def require_config(value: str, name: str) -> str:
    if not value:
        raise RuntimeError(f"Missing required config value: {name}")
    return value
