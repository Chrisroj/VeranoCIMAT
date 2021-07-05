# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

from dash.dependencies import Input, Output
from sqlalchemy import create_engine

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

# Create engine with the next sintax: dialect+driver://username:password@host:port/database
# Aquí debería cambiar el root y pasword por json checa TSC
db_connection_str = "mysql://root:12345akira@localhost/prueba_cryptos"
db_connection = create_engine(db_connection_str) # DB connection 

# Query data
query = "SELECT * FROM price_usd LIMIT 10000"
cryptoCoins = pd.read_sql(query, con = db_connection)


app.layout = html.Div(children=[
    
    # Title
    html.H1(children='Practicando Graficos'),
    
    # Brief Description
    html.Div(children='''
        Esta es una práctica de los gráficos de cryptos
    '''),
    
    # Select Crypto Name
    dcc.Dropdown(
                id = 'crypto-name',
                options = [{'label':i, 'value':i} for i in cryptoCoins.columns[2:]],
                value = 'bitcoin',
                clearable = False # Prevent the clearing
        ),
    
    # Plot
    dcc.Graph(id = 'serie-choose')
])
             
             
# Callback
@app.callback(
    Output(component_id = 'serie-choose', component_property = 'figure'),
    Input(component_id = 'crypto-name', component_property = 'value'))

def update_figure(selected_crypto):
    # Updating the time series
    fig = px.line(cryptoCoins, x = 'time', y = str(selected_crypto))
    fig.update_layout(transition_duration = 100)
    return fig
             
if __name__ == '__main__':
    app.run_server(debug=True)