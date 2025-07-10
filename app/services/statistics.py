from typing import List, Dict
from app.db.models import BitcoinPrice
from datetime import timedelta
import numpy as np

def calculate_statistics(prices: List[BitcoinPrice]) -> Dict:
    """
    Calculates key statistics from a list of Bitcoin prices.
    """
    if not prices or len(prices) < 2:
        return {}

    # Sort prices by date to ensure chronological order
    price_data = sorted([(p.dateAdd, p.price) for p in prices if p.price > 0], key=lambda x: x[0])
    
    if not price_data:
        return {}

    dates, price_values = zip(*price_data)
    
    # Latest price
    latest_price = price_values[-1]
    latest_date = dates[-1]

    # ATH (All-Time High)
    ath_price = max(price_values)
    ath_date = dates[price_values.index(ath_price)]
    days_since_ath = (latest_date - ath_date).days

    # Average price for the period
    average_price = np.mean(price_values)

    # Moving averages
    sma_50 = np.mean(price_values[-50:]) if len(price_values) >= 50 else None
    sma_200 = np.mean(price_values[-200:]) if len(price_values) >= 200 else None

    # Performance over periods
    performance = {}
    for days_ago in [365]:
        target_date = latest_date - timedelta(days=days_ago)
        past_price_point = min(price_data, key=lambda x: abs(x[0] - target_date))
        past_price = past_price_point[1]
        if past_price > 0:
            performance[days_ago] = ((latest_price - past_price) / past_price) * 100
        else:
            performance[days_ago] = None

    change_from_ath_percent = ((latest_price - ath_price) / ath_price) * 100 if ath_price > 0 else 0

    return {
        "latest_price": latest_price,
        "latest_date": latest_date,
        "ath_price": ath_price,
        "ath_date": ath_date,
        "days_since_ath": days_since_ath,
        "average_price": average_price,
        "sma_50": sma_50,
        "sma_200": sma_200,
        "performance_365d": performance.get(365),
        "change_from_ath_percent": change_from_ath_percent,
    } 