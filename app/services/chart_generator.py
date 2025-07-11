import plotly.graph_objects as go
import numpy as np
from typing import List
from app.db.models import BitcoinPrice
from app.services.statistics import calculate_statistics
import logging
import html
from datetime import datetime

def create_logarithmic_spiral_chart(prices: List[BitcoinPrice]) -> str:
    try:
        if not prices:
            return "<h2>No data available</h2>"
        
        price_values = [price.price for price in prices]
        dates = [price.dateAdd for price in prices]
        n = len(price_values)
        if n < 2:
            return "<h2>Insufficient data for chart</h2>"
        
        halving_dates = [
            datetime(2012, 11, 28),  # 1st halving
            datetime(2016, 7, 9),    # 2nd halving
            datetime(2020, 5, 11),   # 3rd halving
            datetime(2024, 4, 20)    # 4th halving
        ]

        events_dates = [
            {"date": datetime(2010, 5, 22), "name": "Bitcoin Pizza Day"},
            {"date": datetime(2010, 12, 12), "name": "Satoshi Nakamoto Disappearance"},
            {"date": datetime(2014, 2, 28), "name": "Mt. Gox crash"},
            {"date": datetime(2017, 8, 1), "name": "Bitcoin Cash hard fork"},
            {"date": datetime(2022, 5, 9), "name": "The Fall of Terra"},
            {"date": datetime(2022, 11, 10), "name": "FTX collapse"},
            {"date": datetime(2024, 1, 10), "name": "ETF Bitcoin approval"},
        ]
        
        epsilon = 1e-2 # Use a small constant for prices that are zero or less
        price_for_log = np.array([p if p > 0 else epsilon for p in price_values])
        r = np.log10(price_for_log)
        
        start_date = min(dates)
        end_date = max(dates)
        days_since_start = np.array([(d - start_date).days for d in dates])
        
        theta = days_since_start * (360 / 1461)

        halving_indices = []
        for i, halving_date in enumerate(halving_dates):
            date_differences = [abs((d - halving_date).days) for d in dates]
            min_diff_index = date_differences.index(min(date_differences))
            if min(date_differences) <= 1:
                halving_indices.append({
                    "index": min_diff_index,
                    "date": halving_date,
                    "number": i + 1
                })

        event_indices = []
        for event in events_dates:
            date_differences = [abs((d - event["date"]).days) for d in dates]
            min_diff_index = date_differences.index(min(date_differences))
            if min(date_differences) <= 1:
                event_indices.append({
                    "index": min_diff_index,
                    "name": event["name"],
                    "date": event["date"]
                })

        # Get ATH from statistics service
        stats = calculate_statistics(prices)
        ath_price = stats.get("ath_price")
        ath_date = stats.get("ath_date")
        
        ath_index = None
        if ath_price and ath_date:
            for i, (d, p) in enumerate(zip(dates, price_values)):
                if d == ath_date and p == ath_price:
                    ath_index = i
                    break

        usd_ticks = [1, 10, 100, 1_000, 10_000, 100_000, 1_000_000]
        r_ticks = [np.log10(v) for v in usd_ticks if v <= price_for_log.max() * 1.5]
        r_tick_labels = [f"{v:,}" for i, v in enumerate(usd_ticks) if i < len(r_ticks)]

        year_tick_labels = ['2025', '2022', '2023', '2024']
        year_angles = [0, 90, 180, 270]

        hover_texts = []
        for d, p in zip(dates, price_values):
            hover_texts.append(
                f"<b>Date:</b> {d.strftime('%Y-%m-%d')}<br>"
                f"<b>Price:</b> ${p:,.2f}<br>"
            )

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=r,
            theta=theta,
            mode='lines+markers',
            name='Bitcoin Price',
            line=dict(color='#F7931A', width=2),
            marker=dict(size=3, color='#F7931A', line=dict(color='#F7931A', width=1)),
            hoverinfo='text',
            text=hover_texts,
            hovertemplate='%{text}<extra></extra>'
        ))
        
        for halving in halving_indices:
            i = halving["index"]
            d, p = dates[i], price_values[i]
            
            halving_hover_text = (
                f"<b>🌕 HALVING #{halving['number']}</b><br>"
                f"<b>Date:</b> {d.strftime('%Y-%m-%d')}<br>"
                f"<b>Price:</b> ${p:,.2f}<br>"
            )
            
            fig.add_trace(go.Scatterpolar(
                r=[r[i]],
                theta=[theta[i]],
                mode='markers',
                name=f"Halving #{halving['number']} - {halving['date'].strftime('%Y-%m-%d')}",
                marker=dict(
                    size=14, 
                    color='white', 
                    line=dict(color='#F7931A', width=2),
                    symbol='diamond'
                ),
                hoverinfo='text',
                text=[halving_hover_text],
                hovertemplate='%{text}<extra></extra>'
            ))

        for event in event_indices:
            i = event["index"]
            d, p = dates[i], price_values[i]
            
            event_hover_text = (
                f"<b>{event['name'].upper()}</b><br>"
                f"<b>Date:</b> {d.strftime('%Y-%m-%d')}<br>"
                f"<b>Price:</b> ${p:,.2f}<br>"
            )
            
            fig.add_trace(go.Scatterpolar(
                r=[r[i]],
                theta=[theta[i]],
                mode='markers',
                name=f"{event['name']} - {d.strftime('%Y-%m-%d')}",
                marker=dict(
                    size=14,
                    color='#00FFFF',
                    line=dict(color='#ffffff', width=1),
                    symbol='square'
                ),
                hoverinfo='text',
                text=[event_hover_text],
                hovertemplate='%{text}<extra></extra>'
            ))

        if ath_index is not None and ath_price and ath_date:
            ath_hover_text = (
                f"<b>ALL-TIME HIGH</b><br>"
                f"<b>Date:</b> {ath_date.strftime('%Y-%m-%d')}<br>"
                f"<b>Price:</b> ${ath_price:,.2f}<br>"
            )
            
            fig.add_trace(go.Scatterpolar(
                r=[r[ath_index]],
                theta=[theta[ath_index]],
                mode='markers',
                name=f"ATH - {ath_date.strftime('%Y-%m-%d')}",
                marker=dict(
                    size=24,
                    color='#FFFF00',
                    line=dict(color='#000000', width=2),
                    symbol='triangle-up'
                ),
                hoverinfo='text',
                text=[ath_hover_text],
                hovertemplate='%{text}<extra></extra>'
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    showgrid=True,
                    gridcolor='#2a2a2a',
                    tickfont={'size': 12, 'color': '#ffffff', 'family': 'Inter, sans-serif'},
                    tickvals=r_ticks,
                    ticktext=r_tick_labels,
                    ticksuffix=' USD',
                    range=[0, np.log10(max(usd_ticks))],
                    linecolor='#2a2a2a',
                    showline=True,
                    linewidth=1,
                ),
                angularaxis=dict(
                    showgrid=True,
                    gridcolor='#2a2a2a',
                    tickfont={'size': 12, 'color': '#ffffff', 'family': 'Inter, sans-serif'},
                    tickvals=year_angles,
                    ticktext=year_tick_labels,
                    rotation=90,
                    direction='clockwise',
                    linecolor='#2a2a2a',
                    showline=True,
                    linewidth=1,
                ),
                bgcolor='#111111'
            ),
            showlegend=True,
            legend=dict(
                x=0.02,
                y=0.98,
                bgcolor='rgba(26, 26, 26, 0.9)',
                bordercolor='#2a2a2a',
                borderwidth=1,
                font=dict(
                    family='Inter, sans-serif',
                    color='#ffffff',
                    size=16
                ),
                itemsizing='constant',
                itemwidth=30
            ),
            height=None,
            width=None,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            autosize=True,
            margin=dict(l=10, r=10, t=40, b=40),
            font=dict(family='Inter, sans-serif', color='#ffffff', size=10),
            hoverlabel=dict(
                bgcolor='#1a1a1a',
                bordercolor='#2a2a2a',
                font=dict(family='Inter, sans-serif', color='#ffffff', size=12)
            )
        )
        
        html_output = fig.to_html(
            include_plotlyjs=True,
            full_html=False,
            config={
                'displayModeBar': False, 
                'displaylogo': False,
                'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': 'bitcoin-spiral-chart',
                    'height': 800,
                    'width': 1200,
                    'scale': 2
                }
            },
            default_height='90vh',
            default_width='100vw'
        )
        
        mobile_css = """
        <style>
        @media (max-width: 768px) {
            .legend {
                display: none !important;
            }
            .plotly .legend {
                display: none !important;
            }
            .js-plotly-plot .plotly .legend {
                display: none !important;
            }
        }
        </style>
        <script>
        // Additional JavaScript to hide legend on mobile
        document.addEventListener('DOMContentLoaded', function() {
            function hideLegendOnMobile() {
                if (window.innerWidth <= 768) {
                    const plotlyDiv = document.querySelector('.js-plotly-plot');
                    if (plotlyDiv) {
                        Plotly.relayout(plotlyDiv, {'showlegend': false});
                    }
                } else {
                    const plotlyDiv = document.querySelector('.js-plotly-plot');
                    if (plotlyDiv) {
                        Plotly.relayout(plotlyDiv, {'showlegend': true});
                    }
                }
            }
            
            // Initial check
            hideLegendOnMobile();
            
            // Check on window resize
            window.addEventListener('resize', hideLegendOnMobile);
        });
        </script>
        """
        
        return mobile_css + html_output
    except Exception as e:
        logging.error(f"Error creating chart: {e}")
        return f"<h2>Error generating chart: {html.escape(str(e))}</h2>" 