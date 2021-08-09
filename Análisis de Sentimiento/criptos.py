# -*- coding: utf-8 -*-
"""
Created on Mon Jul  5 14:46:36 2021

@author: Christopher
"""
import numpy as np
import pandas as pd
import datetime as dt
import re

from statsmodels.tsa.stattools import acf, pacf
import plotly.graph_objects as go


# Convert client.get_klines to data frame
def klines_to_df(data):  
    # Columns names https://www.programcreek.com/python/?CodeExample=get+klines
    col_names = ['Open_time', 'Open', 'High', 'Low', 'Close', 'Volume', 
                 'Close_time', 'Quote_asset_volume', 'Number_of_trades', 
                'Taker_buy_base_asset_volume', 'Taker_buy_quote_asset_volume', 'Can_be_ignored']
    data = pd.DataFrame(data, columns = col_names)
    
    # Setting data types
    data["Open_time"] = data["Open_time"].map(lambda time: dt.datetime.fromtimestamp(time/1000))
    data["Close_time"] = data["Close_time"].map(lambda time: dt.datetime.fromtimestamp(time/1000))
    data['Open'] = data['Open'].astype(np.float32)
    data['High'] = data['High'].astype(np.float32)
    data['Low'] = data['Low'].astype(np.float32)
    data['Close'] = data['Close'].astype(np.float32)
    data['Number_of_trades'] = data['Number_of_trades'].astype(np.int32)
    
    return data

# Clean and Tokenize a text
def clean_tokenize(text, stop_words):
    # To lowercase
    new_text = text.lower()
    
    # Drop http web pages
    new_text = re.sub('http\S+', ' ', new_text)
    
    # Drop @users
    new_text = re.sub('@[^\s]+', ' ', new_text)
    
    # Drop punctuation marks
    regex = '[\\!\\"\\#\\$\\%\\&\\\'\\(\\)\\*\\+\\,\\-\\.\\/\\:\\;\\<\\=\\>\\?\\@\\[\\\\\\]\\^_\\`\\{\\|\\}\\~]'
    new_text = re.sub(regex , ' ', new_text)
    
    # Drop numbers
    new_text = re.sub("\d+", ' ', new_text)
    
    # Drop multiple spaces
    new_text = re.sub("\\s+", ' ', new_text)
    
    # Tokenization
    new_text = new_text.split(sep = ' ')
    
    # Drop token length less than 3 and with a stop-word
    new_text = [token for token in new_text if (len(token) > 2) and (token not in stop_words)]
    
    return(new_text)

# Function to create ACF in plotly
def create_corr_plot(series, plot_pacf=False):
    corr_array = pacf(series.dropna(), alpha=0.05) if plot_pacf else acf(series.dropna(), alpha=0.05)
    lower_y = corr_array[1][:,0] - corr_array[0]
    upper_y = corr_array[1][:,1] - corr_array[0]

    fig = go.Figure()
    [fig.add_scatter(x=(x,x), y=(0,corr_array[0][x]), mode='lines',line_color='#3f3f3f') 
     for x in range(len(corr_array[0]))]
    fig.add_scatter(x=np.arange(len(corr_array[0])), y=corr_array[0], mode='markers', marker_color='#1f77b4',
                   marker_size=12)
    fig.add_scatter(x=np.arange(len(corr_array[0])), y=upper_y, mode='lines', line_color='rgba(255,255,255,0)')
    fig.add_scatter(x=np.arange(len(corr_array[0])), y=lower_y, mode='lines',fillcolor='rgba(32, 146, 230,0.3)',
            fill='tonexty', line_color='rgba(255,255,255,0)')
    fig.update_traces(showlegend=False)
    fig.update_xaxes(range=[-1,42])
    fig.update_yaxes(zerolinecolor='#000000')
    
    title='Partial Autocorrelation (PACF)' if plot_pacf else 'Autocorrelation (ACF)'
    fig.update_layout(title=title)
    return fig

