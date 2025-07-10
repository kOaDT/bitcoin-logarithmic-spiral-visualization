from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import List, Optional
import logging
from .models import BitcoinPrice

def get_prices(db: Session, days: Optional[int] = None) -> List[BitcoinPrice]:
    """
    Fetches Bitcoin prices from the database.
    
    Can be filtered by the number of days from the present.
    """
    try:
        query = db.query(BitcoinPrice).order_by(BitcoinPrice.dateAdd.asc())
        if days:
            start_date = datetime.now(timezone.utc) - timedelta(days=days)
            query = query.filter(BitcoinPrice.dateAdd >= start_date)
        return query.all()
    except Exception as e:
        logging.error(f"Error fetching Bitcoin prices: {e}")
        raise 