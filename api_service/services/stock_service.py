import logging

from api_service.clients.stock_client import StockClient
from api_service.repositories.stock_repository import StockRepository

logger = logging.getLogger(__name__)


class StockService:
    """Handles business logic for stock queries."""

    @staticmethod
    def process_stock_query(user, stock_code):
        """Fetches stock data from `stock_service` and saves it to the database."""
        stock_data = StockClient.fetch_stock_data(stock_code)
        if not stock_data:
            logger.warning(f"Stock data not found for: {stock_code}")
            return None

        StockRepository.save_stock_query(user.id, stock_data)
        logger.info(f"Stock data for {stock_code} saved successfully.")

        return {
            "symbol": stock_data["symbol"],
            "company_name": stock_data["name"],
            "quote": stock_data["close"],
        }
