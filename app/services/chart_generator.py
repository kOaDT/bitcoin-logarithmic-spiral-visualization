import plotly.graph_objects as go
import numpy as np
from typing import List
from app.db.models import BitcoinPrice
import logging
import html

def create_logarithmic_spiral_chart(prices: List[BitcoinPrice]) -> str:
    try:
        if not prices:
            return "<h2>No data available</h2>"
        
        price_values = [price.price for price in prices]
        dates = [price.dateAdd for price in prices]
        n = len(price_values)
        if n < 2:
            return "<h2>Insufficient data for chart</h2>"
        
        epsilon = 1e-2 # Use a small constant for prices that are zero or less
        price_for_log = np.array([p if p > 0 else epsilon for p in price_values])
        r = np.log10(price_for_log)
        
        start_date = min(dates)
        end_date = max(dates)
        days_since_start = np.array([(d - start_date).days for d in dates])
        
        # 1461 days is approx 4 years (one halving cycle)
        theta = days_since_start * (360 / 1461)

        usd_ticks = [1, 10, 100, 1_000, 10_000, 100_000, 1_000_000]
        r_ticks = [np.log10(v) for v in usd_ticks if v <= price_for_log.max() * 1.5]
        r_tick_labels = [f"{v:,}" for i, v in enumerate(usd_ticks) if i < len(r_ticks)]

        last_year = end_date.year
        year_tick_labels = [str(last_year - i) for i in range(4)]
        year_angles = [i * (360 / 4) for i in range(4)] # Quarterly labels

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
            showlegend=False,
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
        
        return fig.to_html(
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
    except Exception as e:
        logging.error(f"Error creating chart: {e}")
        return f"<h2>Error generating chart: {html.escape(str(e))}</h2>" 