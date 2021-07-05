# -*- coding: utf-8 -*-
"""
Created on Sat Jun 26 19:52:46 2021

@author: ferro
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

from sqlalchemy import create_engine

# Create engine with the next sintax: dialect+driver://username:password@host:port/database
# Aquí debería cambiar el root y pasword por json checa TSC
db_connection_str = "mysql://root:12345akira@localhost/prueba_cryptos"
db_connection = create_engine(db_connection_str) # DB connection 

# Query data
crypto = pd.read_sql("SELECT id, time, bitcoin FROM price_usd", con = db_connection)
crypto

df = px.data.stocks()
fig = px.line(df, x='date', y="GOOG")
fig.show()
