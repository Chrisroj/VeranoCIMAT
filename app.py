# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
import os
import flask
import glob

from cryptos import create_corr_plot

pd.options.plotting.backend = "plotly" # To use plotly 

from dash.dependencies import Input, Output
from sqlalchemy import create_engine

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')

fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                open=df['AAPL.Open'],
                high=df['AAPL.High'],
                low=df['AAPL.Low'],
                close=df['AAPL.Close'])])


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Path
path = r"C:\Users\ferro\Desktop\VeranoCIMAT\Análisis de Sentimiento\data_dash"

# Lista de cryptos
cryptos = ["BTC", "ETH", "LTC", "ADA", "SHIB", "XRP", "MANA"]

# Tweets mensuales
activity = pd.read_csv(os.path.join(path, "2_activity.csv"), index_col="month")

# Palabras frecuentes
frequent_words = pd.read_csv(os.path.join(path, "3_frequent_words.csv")) 
users = frequent_words["user"].unique()

# Images wordcloud
image_directory = os.path.join(path, "4_wordcloud")
list_of_images = [img.split(".")[0] for img in os.listdir(os.path.join(path, "4_wordcloud"))]
static_image_route = '/static/'

# Promedio de palabras
mean_words = pd.read_csv(os.path.join(path, "5_mean_words.csv"), index_col = "user")

# Score del análsis de sentimiento
sentiment_score = pd.read_csv(os.path.join(path, "6_sentiment_score.csv"), index_col = "day")

# Retornos cuadraticos
retornos_2 = pd.read_csv(os.path.join(path, "1_BTC.csv"), 
                         usecols = ["Close", "Open_time"], index_col= "Open_time").pct_change().dropna()**2


app.layout = html.Div(children=[
    
    # Title
    html.H1(children='Volatilidad BTC'),
    
    # Brief Description
    html.Div(children='''
        Los precios del Bitcoin fueorn extraidos con la API  de Binance del periodo 01/01/2018 al 01/06/2021 
    '''),
    
    
    html.Div([
            # Select Crypto
            dcc.Dropdown(
                id='crypto',
                options=[{'label': i, 'value': i} for i in cryptos],
                value='BTC',
                clearable = False
            ),
            dcc.RadioItems(
                id='tipo-grafica',
                options= [{'label':i, 'value':i} for i in ["Lineal", "Velas Japonesas"]],
                value='Lineal',
                labelStyle={'display': 'inline-block', 'marginTop': '5px'}
            )
        ],
        style={'width': '49%', 'display': 'inline-block'}),   
    
    # Plot
    dcc.Graph(id = 'serie-choose'),
    
    # Tweets Mensuales
    html.H2(children='Tweets Mensuales por Usuario'),
    
    
    # Descripción
    html.Div(children='''
        Cantidad de tweets(dónde se menciona al bitcoin) mensuales para cada usuario.
    '''),
    
    # Plot
    dcc.Graph(
        id = 'month-activity',
        figure = activity.plot()
              ),
    
    html.H2(children='Palabras frecuentes'),
    
    html.Div(children='''
        Top 10 palabras más usadas por los usuarios cuando hacen un tweet relacionado al BTC. 
    '''),
    
   # Bar of Frequencies
    dcc.Dropdown(
                    id='user',
                    options=[{'label': i, 'value': i} for i in users],
                    value = 'forbes',
                    clearable = False),
    
    dcc.Graph(
        id = 'frequent-words'
              ),
    
    html.H2(children='Wordcloud'),
    html.Div(children='''
        Wordcloud de las palabras en cada tweet de los usuarios
    '''),
    # WordCloud
    dcc.Dropdown(
        id='image-dropdown',
        options=[{'label': i, 'value': i} for i in list_of_images],
        value=list_of_images[0]
    ),
    
    html.Img(id='image'),
    
    html.H2(children ="Promedio de palabras por tweet"),
    
    # Promedio de palabras por tweet
    dcc.Graph(
        id = 'mean-word',
        figure = mean_words.plot.bar()
              ),
    
    html.H2(children ="Análisis de Sentimiento"),
    
    html.Div(children='''
        Scores diario acerca del sentimiento hacia el BTC, tomamos el promedio, el mínimo y máximo valor del score del día.
    '''),
    
    # Promedio de palabras por tweet
    dcc.Graph(
        id = 'sentiment-score',
        figure = sentiment_score.plot()
              ),
    
    html.H2(children ="Retornos cuadraticos"),
    
        # Promedio de palabras por tweet
    dcc.Graph(
        id = 'return-squares',
        figure = create_corr_plot(retornos_2["Close"].reset_index(drop = True))
              )    
            

    
])

             
             
# Serie de los precios del BTC
@app.callback(
    Output(component_id = 'serie-choose', component_property = 'figure'),
    [Input(component_id = 'tipo-grafica', component_property = 'value'),
    Input(component_id = 'crypto', component_property = 'value')])
def update_figure(tipo_grafica, tipo_crypto):
    # Updating the time series
    prices = prices = pd.read_csv(os.path.join(path, "1_" + tipo_crypto + ".csv"))
    if tipo_grafica == "Lineal":
        fig = prices.plot(x = "Open_time", y = "Close")
        fig.update_layout(transition_duration = 100,
                          xaxis_title = "Fecha",
                          yaxis_title = "USDT")
    elif tipo_grafica == "Velas Japonesas":
        fig = go.Figure(data=[go.Candlestick(x=prices['Open_time'],
                open=prices['Open'],
                high=prices['High'],
                low=prices['Low'],
                close=prices['Close'])])
    return fig

@app.callback(
    Output(component_id = 'frequent-words', component_property = 'figure'),
    Input(component_id = 'user', component_property = 'value'))
def update_figure_user(user):
    tweets_freq = frequent_words[frequent_words["user"] == user].groupby(by = "tweet")["tweet"].count().sort_values(ascending = False)
    fig = tweets_freq[0:10].plot.bar(title = user)
    fig.update_layout(xaxis_title = "Palabra",
                      yaxis_title = "Frecuencia")
    return fig

@app.callback(
    dash.dependencies.Output('image', 'src'),
    [dash.dependencies.Input('image-dropdown', 'value')])
def update_image_src(value):
    return static_image_route + value + ".png"

# Add a static image route that serves images from desktop
# Be *very* careful here - you don't want to serve arbitrary files
# from your computer or server
@app.server.route('{}<image_path>.png'.format(static_image_route))
def serve_image(image_path):
    image_name = '{}.png'.format(image_path)
    if image_name not in [img + ".png" for img in list_of_images]:
        raise Exception('"{}" is excluded from the allowed static files'.format(image_path))
    return flask.send_from_directory(image_directory, image_name)

             
if __name__ == '__main__':
    app.run_server(debug=True)