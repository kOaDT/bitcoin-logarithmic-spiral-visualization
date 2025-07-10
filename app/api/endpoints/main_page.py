from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
import logging
import json

from app.db.session import get_db
from app.db.crud import get_prices
from app.services.chart_generator import create_logarithmic_spiral_chart
from app.services.statistics import calculate_statistics
from app.core.config import settings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)

@router.get("/")
async def root(request: Request, days: Optional[int] = None, db: Session = Depends(get_db)):
    try:
        prices = get_prices(db, days=days)
        chart_html_content = ""
        stats_html_content = ""
        
        if not prices:
            chart_html_content = "<div style='width:100%;height:100%;display:flex;align-items:center;justify-content:center;'><h2>No Bitcoin price data available</h2></div>"
            stats_html_content = "<p>No data to compute statistics.</p>"
        else:
            chart_html_content = create_logarithmic_spiral_chart(prices)
            stats = calculate_statistics(prices)
            
            stats_html_content = f"""
                <div class="stat-item">
                    <span>Current Price</span>
                    <strong>${stats.get('latest_price', 0):,.2f}</strong>
                </div>
                <div class="stat-item">
                    <span>All-Time High</span>
                    <strong>${stats.get('ath_price', 0):,.2f}</strong>
                </div>
                <div class="stat-item">
                    <span>Days Since ATH</span>
                    <strong>{stats.get('days_since_ath', 'N/A')}</strong>
                </div>
                <div class="stat-item">
                    <span>Change from ATH</span>
                    <strong style="color: {'#ff4d4d' if stats.get('change_from_ath_percent', 0) < 0 else '#4caf50'};">{stats.get('change_from_ath_percent', 0):.2f}%</strong>
                </div>
                <div class="stat-item">
                    <span>Performance (1Y)</span>
                    <strong style="color: {'#ff4d4d' if stats.get('performance_365d', 0) < 0 else '#4caf50'};">
                        {f"{stats['performance_365d']:.2f}%" if stats.get('performance_365d') is not None else 'N/A'}
                    </strong>
                </div>
                <div class="stat-item">
                    <span>SMA 50D</span>
                    <strong>{f"${stats['sma_50']:,.2f}" if stats.get('sma_50') is not None else 'N/A'}</strong>
                </div>
                <div class="stat-item">
                    <span>SMA 200D</span>
                    <strong>{f"${stats['sma_200']:,.2f}" if stats.get('sma_200') is not None else 'N/A'}</strong>
                </div>
            """

        base_url = str(request.base_url).rstrip('/')
        page_url = f"{base_url}?days={days}" if days else base_url
        if not page_url.endswith('/'):
            page_url += '/'

        title = "Bitcoin Logarithmic Spiral Chart - Live BTC Price Visualization"
        description = "Visualize Bitcoin's price history on a logarithmic spiral chart. Live data, statistical analysis, and long-term trends for BTC."
        og_image_url = f"{base_url}static/og-image.png"

        json_ld_data = {
          "@context": "https://schema.org",
          "@type": "WebApplication",
          "name": title,
          "url": page_url,
          "description": description,
          "applicationCategory": "FinanceApplication",
          "operatingSystem": "All",
          "offers": {
            "@type": "Offer",
            "price": "0"
          },
          "screenshot": og_image_url,
          "creator": {
            "@type": "Organization",
            "name": "Bitcoin Logarithmic Spiral"
          }
        }

        context = {
            "request": request,
            "title": title,
            "description": description,
            "page_url": page_url,
            "og_image_url": og_image_url,
            "json_ld_data": json.dumps(json_ld_data, indent=2),
            "chart_html_content": chart_html_content,
            "stats_html_content": stats_html_content,
            "google_analytics_id": settings.GOOGLE_ANALYTICS_ID,
        }
        
        return templates.TemplateResponse("index.html", context)
    except Exception as e:
        logger.error(f"Error on root endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") 