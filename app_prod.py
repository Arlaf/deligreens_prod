#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 10:11:30 2018

@author: arnaud
"""

from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd

from app import app
from models import mod_orders, mod_sells_analysis as sells
from views import views_prod

orders = mod_orders.OrdersClass()

app.layout = views_prod.generate_html()

@app.callback(
    Output('df_orders_init_storage', 'children'),
    [Input('import_button', 'n_clicks')],
    [State('date_import_orders', 'start_date')])
def data_collection(n, debut):
#    yield pd.DataFrame() # On renvoie au serveur quelque chose dès le début pour éviter le timeout si les calculs prennent plus de 30 sec
    df_orders = orders.get_data(debut)
    return df_orders.to_json(date_format = 'iso', orient = 'split')

@app.callback(
    Output('df_orders_storage', 'children'),
    [Input('df_orders_init_storage', 'children'),
     Input('box_rm_teammates', 'values'),
     Input('date_import_orders', 'start_date'),
     Input('date_import_orders', 'end_date')])
def filter_data(df_orders_json, rm_teammates, start, end):
    df_orders = orders.filtrage(df_orders_json, rm_teammates, start, end)
    return df_orders.to_json(date_format = 'iso', orient = 'split')

@app.callback(
    Output('collection_storage', 'children'))
def get_collections_list():
    return orders.df_collections.to_json(orient='split')

@app.callback(
    Output('collections_clecklist', 'children'),
    [Input('import_button', 'n_clicks')]) # Inutile mais je ne sais pas faire la même chose sans Input
def show_collections_list(n):
    return orders.collections.create_collections_dropdown()

@app.callback(
    Output('graph_sells_evolution', 'figure'),
    [Input('df_orders_storage', 'children'),
     Input('collections_clecklist', 'value')])
def show_graph_sells_evolution(df_orders_json, collections):
    figure = sells.construct_graph_sells_evolution(df_orders_json, collections)
    return figure
    
if __name__ == '__main__':
    app.run_server(debug=True)