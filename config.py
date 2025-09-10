# src/config.py
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# Load from .env file if present
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
    logging.info(f".env loaded from {env_path}")
else:
    logging.warning(".env file not found, using system environment variables")

# Read API keys
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

# Check keys
if not BINANCE_API_KEY or not BINANCE_API_SECRET:
    logging.error("❌ Binance API key/secret missing. Please set them in .env")
else:
    logging.info("✅ Binance API key/secret loaded successfully")

# Switch between testnet and mainnet
USE_TESTNET = os.getenv("USE_TESTNET", "true").lower() == "true"

# Spot endpoints
BASE_URL_SPOT = (
    "https://testnet.binance.vision/api" if USE_TESTNET
    else "https://api.binance.com"
)

logging.info(f"Using {'Spot Testnet' if USE_TESTNET else 'Spot Mainnet'}: {BASE_URL_SPOT}")

# For backward compatibility with Futures, if needed
BASE_URL_FUTURES = (
    "https://testnet.binancefuture.com" if USE_TESTNET
    else "https://fapi.binance.com"
)

if __name__ == "__main__":
    logging.info(f"BINANCE_API_KEY: {BINANCE_API_KEY[:5]}... (hidden)")
    logging.info(f"BINANCE_API_SECRET: {BINANCE_API_SECRET[:5]}... (hidden)")
    logging.info(f"BASE_URL_SPOT: {BASE_URL_SPOT}")
    logging.info(f"BASE_URL_FUTURES: {BASE_URL_FUTURES}")
