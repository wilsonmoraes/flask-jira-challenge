import logging

from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource

from api_service.extensions import cache
from api_service.repositories.stock_repository import StockRepository
from api_service.services.auth_service import AuthService, jwt_admin_required
from api_service.services.stock_service import StockService

logger = logging.getLogger(__name__)


class StockQuery(Resource):
    """Handles user stock queries."""

    @jwt_required()
    def get(self):
        logger.info("Received stock query request.")

        user = AuthService.get_authenticated_user()

        stock_code = request.args.get("q")
        if not stock_code:
            logger.warning("Missing stock query parameter.")
            return {"message": "Missing stock query parameter"}, 400

        stock_data = StockService.process_stock_query(user, stock_code)
        if not stock_data:
            return {"message": "Stock not found"}, 404

        cache.delete(f"history:{user.id}")
        cache.delete("stats")

        return stock_data, 200


class History(Resource):
    """Returns queries made by the current authenticated user."""

    @jwt_required()
    def get(self):
        user = AuthService.get_authenticated_user()

        cache_key = f"history:{user.id}"
        cached = cache.get(cache_key)
        if cached:
            return cached, 200

        history = StockRepository.get_user_history(user.id)
        result = [
            {
                "date": query.date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "symbol": query.symbol,
                "company_name": query.company_name,
                "open": query.open,
                "high": query.high,
                "low": query.low,
                "close": query.close,
            }
            for query in history
        ]

        cache.set(cache_key, result)

        return result, 200


class Stats(Resource):
    """Allows admin users to see the most queried stocks."""

    @jwt_admin_required
    def get(self):
        cache_key = "stats"
        cached = cache.get(cache_key)
        if cached:
            return cached, 200

        stats = StockRepository.get_top_stocks()

        result = [{"stock": stock[0], "times_requested": stock[1]} for stock in stats]

        cache.set(cache_key, result)
        return result, 200
