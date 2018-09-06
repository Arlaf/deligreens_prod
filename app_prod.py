#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 10:11:30 2018

@author: arnaud
"""

from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc

from app import app
from models import mod_orders
from views import views_prod

orders = mod_orders.OrdersClass()

app.layout = views_prod.generate_html()

@app.callback(
    Output('output', 'children'),
    [Input('button1', 'n_clicks')])
def count_clicks(n):
    return [html.P(f'''Vous avez cliqué {n} fois, bravo ! Cliquez une fois de plus pour arriver à {orders.func_test(n)}, courage !'''),
            html.P(orders.df_orders)]
    
if __name__ == '__main__':
    app.run_server(debug=True)