# import pandas
import pandas as pd
import os
import pathlib
import numpy as np
import datetime as dt
import dash
import dash_core_components as dcc
import dash_html_components as html

from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from scipy.stats import rayleigh
import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import iplot
from plotly.subplots import make_subplots

from cassandrautils import *

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Dash"

server = app.server

app_color = {"graph_bg": "#082255", "graph_line": "#007ACE"}

app.layout = html.Div(
    [
        # header
        html.Div(
            [
                html.Div(
                    [
                        html.H4("Visualization with Dash", className="app__header__title"),
                        html.P(
                            "This app continually queries Cassandra database and displays live charts based on the current data.",
                            className="app__header__title--grey",
                        ),
                    ],
                    className="app__header__desc",
                ),
                
            ],
            className="app__header",
        ),
        html.Div(
            [
                # weather
                html.Div(
                    [
                        html.Div([
                            html.H5("Temperature line chart (OWM data)"),
                            dcc.Dropdown(
                                id='checklist', 
                                value='temp', 
                                options=[{'value': x, 'label': x} 
                                        for x in ['temp', 'temp_max', 'temp_min', 'feels_like', 'wind']],
                                clearable=False
                            ),
                            dcc.Graph(id="line-chart"),
                        ])
                    ],
                    className="one-half column",
                ),
                # faker
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div([
                                    html.H5("Histogram of age (Faker data)"),
                                    html.P("Number of bin:"),
                                    dcc.Slider(id="num_bin", min=5, max=10, step=1, value=6),
                                    dcc.Graph(id="graph"),
                                ])
                            ],
                            className="graph__container first",
                        ),
                    ],
                    className="one-half column",
                ),
            ],
            className="app__content",
        ),
        html.Div(
            [
                html.Div([
                    dcc.Dropdown(
                        id='pair', 
                        value='BTCUSDT', 
                        options=[{'label': 'BTC/UDST', 'value': 'BTCUSDT'},
                                {'label': 'ETH/UDST', 'value': 'ETHUSDT'}],
                        clearable=False
                    ),
                    dcc.Dropdown(
                        id='interval', 
                        value='1min', 
                        options=[{'label': '1m', 'value': '1min'},
                                {'label': '5m', 'value': '5min'},
                                {'label': '30m', 'value': '30min'},
                                {'label': '1H', 'value': '1H'}],
                        clearable=False
                    ),
                    dcc.Graph(id="graph-crypto"),
                ])
            ],
            className="app__content",
        ),
    ],
    className="app__container",
)

@app.callback(
    Output("line-chart", "figure"), 
    [Input("checklist", "value")])
def update_line_chart(col):
    df = getWeatherDF()
    df['forecast_timestamp'] = pd.to_datetime(df['forecastdate'])
    # Convert Kelvin to Celsius
    df[['feels_like','temp','temp_max','temp_min']] = df[['feels_like','temp','temp_max','temp_min']].transform(lambda x: x - 273.15)
    fig = px.line(df, 
        x="forecast_timestamp", y=col, color='location')
    return fig


@app.callback(
    Output("graph", "figure"), 
    [Input("num_bin", "value")])
def display_color(num_bin):
    df = getFakerDF()
    currentYear = dt.date.today().year
    df['age'] = df['year'].apply(lambda x: int(currentYear-x))
    fig = px.histogram(df['age'], nbins=num_bin, range_x=[0, 100])
    return fig

@app.callback(
    Output("graph-crypto", "figure"), 
    [Input("pair", "value"),Input("interval", "value")])
def display_candlestick(pair, interval):
    df = getBinanceDF()
    # Get the correct pair
    df = df[(df.pair == pair)]

    # Resample the interval
    df = df.set_index('datetime')
    df = df.resample(interval).agg({'open_price': 'first', 
                                    'high_price': 'max', 
                                    'low_price': 'min', 
                                    'close_price': 'last',
                                    'volume': 'sum'})
    df = df.sort_index()
    # Calculate bollinger bands
    WINDOW = 20
    df['sma'] = df['close_price'].rolling(WINDOW, min_periods=1).mean()
    df['std'] = df['close_price'].rolling(WINDOW, min_periods=1).std()

    # Create subplots with 2 rows; top for candlestick price, and bottom for bar volume
    fig = make_subplots(rows = 2, cols = 1, 
                        vertical_spacing=0.1)

    # ----------------
    # Candlestick Plot
    fig.add_trace(go.Candlestick(x = df.index,
                                open = df['open_price'],
                                high = df['high_price'],
                                low = df['low_price'],
                                close = df['close_price'], showlegend=False,
                                name = 'Candlestick'),
                                row = 1, col = 1)

    # Define the parameters for the Bollinger Band calculation
    ma_size = 20
    bol_size = 2

    # Calculate the SMA
    df.insert(0, 'moving_average', df['close_price'].rolling(ma_size).mean())

    # Calculate the upper and lower Bollinger Bands
    df.insert(0, 'bol_upper', df['moving_average'] + df['close_price'].rolling(ma_size).std() * bol_size)
    df.insert(0, 'bol_lower', df['moving_average'] - df['close_price'].rolling(ma_size).std() * bol_size)

    # Remove the NaNs -> consequence of using a non-centered moving average
    df.dropna(inplace=True)

    # Plot the three lines of the Bollinger Bands indicator -> With short amount of time, this can look ugly
    # Moving Average
    fig.add_trace(go.Scatter(x = df.index,
                            y = df['sma'],
                            line_color = 'black',
                            name = 'sma'),
                row = 1, col = 1)

    # Upper Bound
    fig.add_trace(go.Scatter(x = df.index,
                            y = df['sma'] + (df['std'] * 2),
                            line_color = 'gray',
                            line = {'dash': 'dash'},
                            name = 'upper band',
                            opacity = 0.5),
                row = 1, col = 1)

    # Lower Bound fill in between with parameter 'fill': 'tonexty'
    fig.add_trace(go.Scatter(x = df.index,
                            y = df['sma'] - (df['std'] * 2),
                            line_color = 'gray',
                            line = {'dash': 'dash'},
                            fill = 'tonexty',
                            name = 'lower band',
                            opacity = 0.5),
                row = 1, col = 1)

    # Volume Plot
    fig.add_trace(go.Bar(x = df.index, y = df['volume'], showlegend=False), 
                row = 2, col = 1)

    fig.update_layout(title=pair + " : " + interval + " OHLCV",
                    yaxis_title="Price (USDT)")
    # Remove range slider; (short time frame)
    fig.update_xaxes(showticklabels=False, row=1, col=1)
    fig.update(layout_xaxis_rangeslider_visible=False)
    return fig

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=True, dev_tools_ui=True)


