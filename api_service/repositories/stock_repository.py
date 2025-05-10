from api_service.extensions import db
from api_service.models import StockQueryModel


class StockRepository:
    """Handles database operations related to stock queries."""

    @staticmethod
    def save_stock_query(user_id, stock_data):
        """Saves a stock query in the database."""
        stock_query = StockQueryModel(
            user_id=user_id,
            symbol=stock_data["symbol"],
            company_name=stock_data["name"],
            open=stock_data["open"],
            high=stock_data["high"],
            low=stock_data["low"],
            close=stock_data["close"],
        )
        db.session.add(stock_query)
        db.session.commit()

    @staticmethod
    def get_user_history(user_id):
        """Retrieves the stock query history for a user, ordered by date."""
        return StockQueryModel.query.filter_by(user_id=user_id).order_by(StockQueryModel.date.desc()).all()

    @staticmethod
    def get_top_stocks(limit=5):
        """Returns the most queried stocks."""
        return (
            db.session.query(
                StockQueryModel.symbol,
                db.func.count(StockQueryModel.symbol).label("times_requested")
            )
            .group_by(StockQueryModel.symbol)
            .order_by(db.func.count(StockQueryModel.symbol).desc())
            .limit(limit)
            .all()
        )
