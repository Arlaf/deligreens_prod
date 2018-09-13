#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 10:11:30 2018

@author: arnaud
"""
import pandas as pd
from dash.dependencies import Input, Output, State

from app import app
from models import mod_orders, mod_sells_analysis as sells
from views import views_prod

orders = mod_orders.OrdersClass()

app.layout = views_prod.generate_html()

@app.callback(
    Output('df_orders_init_storage', 'children'),
    [Input('import_button', 'n_clicks')],
    [State('date_import_orders', 'start_date'),
     State('date_import_orders', 'end_date')])
def data_collection(n, start, end):
#    yield pd.DataFrame() # On renvoie au serveur quelque chose dès le début pour éviter le timeout si les calculs prennent plus de 30 sec
    # On ne relance l'importation que si la plage de dates saisie ne rentre pas dans ce qui a déjà été importé
    if orders.start_import == None: # On la lance si c'est le lancement de l'application
        orders.get_data(start, end)
    elif (orders.start_import > start) | (orders.end_import < end): # On la lance si une des dates dépasse les précédentes
        orders.get_data(start, end)
    return orders.df_orders.to_json(date_format = 'iso', orient = 'split')

@app.callback(
    Output('df_orders_storage', 'children'),
    [Input('df_orders_init_storage', 'children'),
     Input('box_rm', 'values'),
     Input('date_import_orders', 'start_date'),
     Input('date_import_orders', 'end_date')])
def filter_data(df_orders_json, rm, start, end):
    df_orders = orders.filtrage(df_orders_json, rm, start, end)
    return df_orders.to_json(date_format = 'iso', orient = 'split')

@app.callback(
    Output('collection_storage', 'children'))
def get_collections_list():
    return orders.df_collections.to_json(orient='split')

@app.callback(
    Output('collections_clecklist', 'children'),
    [Input('import_button', 'n_clicks')]) # Inutile mais je n'ai pas trouvé comment faire la même chose sans Input
def show_collections_list(n):
    return orders.collections.create_collections_dropdown()

@app.callback(
    Output('table_evolution_storage', 'children'),
    [Input('df_orders_storage', 'children'),
     Input('radio_duration', 'value'),
     Input('radio_level', 'value')])
def get_table_evolution(df_orders_json, level, duration):
    table = sells.construct_table_evolution(df_orders_json, level, duration) 
    return table.to_json(orient = 'split', date_format = 'iso')

@app.callback(
    Output('graph_sells_evolution', 'figure'),
    [Input('table_evolution_storage', 'children'),
     Input('dropdown_collections', 'value'),
     Input('dropdown_variable', 'value'),
     Input('box_pct', 'values')],
    [State('radio_duration', 'value'),
     State('radio_level', 'value')])
def show_graph_evolution(table_evolution_json, col, variable, pct, duration, level):
    pct = pct == ['pct']
    if col == []:
        return None
    else:
        figure = sells.construct_graph_evolution(table_evolution_json, col, variable, pct, duration, level)
        return figure
    
if __name__ == '__main__':
    app.run_server(debug=True)