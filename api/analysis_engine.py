import plotly.graph_objects as go


def create_plot(df, forecast, forecast_dates, ticker_symbol):
    """
    Creates an interactive Plotly chart of the stock data and forecast.
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Close", line=dict(color="blue")))
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA50"], name="50-Day SMA", line=dict(color="yellow", dash="dash")))
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA200"], name="200-Day SMA", line=dict(color="red", dash="dash")))

    fig.add_trace(
        go.Scatter(
            x=forecast_dates, y=forecast, name="Sentiment-Adjusted Forecast", line=dict(color="green", dash="dot")
        )
    )

    fig.update_layout(
        title=f"Pre-Stocked: {ticker_symbol.upper()} Stock Price Analysis & Forecast",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_dark",
        xaxis_rangeslider_visible=True,
    )

    return fig.to_html(full_html=False)
