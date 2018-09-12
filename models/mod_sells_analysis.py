#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 10 13:22:05 2018

@author: arnaud
"""
import plotly.graph_objs as go
import utilitaires as util
import pandas as pd
import datetime

def col_agg(group):
    # Sommes des ventes HT
    # Dans la bdd core, dans la table line_items, le selling_price_cent est le prix TTC à l'unité
    # Alors que le pre_tax_price est le prix HT mais PAS A L'UNITE, pour toute la quantité commandée
    c1 = group['selling_price_cent_ht'].sum()/100
    # Sommes des cogs HT
    cogs = sum(group['quantity'] * group['buying_price_cent_ht'])/100
    # Marge brute
    c2 = c1 - cogs
    # Nombre de produits vendus
    c3 = group['quantity'].sum()
    colnames = ['sells', 'margin', 'products_sold']
    return pd.Series([c1,c2,c3], index = colnames)

def tot_agg(group, variable):
    c1 = group[variable].sum()
    return pd.Series([c1], index = [variable])

def construct_graph_evolution(df_orders_json, collections, variable, level, duration, pct):
    df_orders = pd.read_json(df_orders_json, orient = 'split', convert_dates = ['created_at', 'week', 'month'])
    # La lecture du json a passé les id_col en float alors on les reconvertit en string
    df_orders['id_col0'] = [str(x)[:-2] for x in df_orders['id_col0']]
    # La lecture du json a passé les dates en timestamp, on les remet en datetime.date
    for date_col in ['created_at', 'week', 'month']:
        df_orders[date_col] = [datetime.date(d.year, d.month, d.day) for d in pd.to_datetime(df_orders[date_col])]
    
    # On ne garde que les collections voulues
    df_orders = df_orders.loc[df_orders['id_col0'].isin(collections), :]
    
    if duration == 'day':
        duration = 'created_at'
    
    if level == 'collections':
        level = 'title0'
    
    # Agregation
    sells = df_orders.groupby([duration,level]).apply(col_agg).unstack(fill_value = 0).stack().reset_index()
    
    if pct:
        totals = sells.groupby(duration).apply(tot_agg, variable = variable).reset_index()[variable]
    
    trace = []
    for lev in sells[level].unique():
        df = sells.loc[sells[level] == lev, :]
        x = [d.strftime('%B %y').capitalize() if duration == 'month' else d.strftime('%d %B %y') for d in df[duration]]
        y = df[variable].reset_index(drop=True)/totals if pct else df[variable]
        # Evolution de la variable étudiée par rapport à la période précédente
        evo = util.format_pct(y - y.shift(1)) if pct else util.format_pct((y - y.shift(1))/y.shift(1))
        for i in range(len(evo)):
            if isinstance(evo[i], str):
                # Si l'evolution est positive alors on rajoute un + devant la valeur
                if not evo[i][0] == '-':
                    evo[i] = '+' + evo[i]
            # Si l'evo est NaN
            else:
                evo[i] = ''
        if pct:
            text = [util.format_pct(y)[i] + ' (' + evo[i] + ') - ' + lev for i in range(len(y))]
        else:
            text = [util.format_entiers(y)[i] + ' (' + evo[i] + ') - ' + lev for i in range(len(y))] if variable == 'products_sold' else [util.format_montant(y)[i] + ' (' + evo[i] + ') - ' + lev for i in range(len(y))]
        temp = go.Bar(
            x = x,
            y = y,
            hoverinfo = 'text',
            text = text,
            name = lev)
        trace += [temp]
    
    if duration == 'week':
        label_dur = 'semaine'
    elif duration == 'created_at':
        label_dur = 'jour'
    else:
        label_dur = 'mois'
        
    if variable == 'sells':
        prep = 'des '
        label_var = 'ventes HT'
    elif variable == 'margin':
        prep = 'de la '
        label_var = 'marge brute'
    else:
        prep = 'du '
        label_var = 'nombre de produits vendus'
    
    layout = {'barmode' : 'stack',
              'title' : 'Evolution ' + prep + label_var + ' par ' + label_dur,
              'yaxis' : {'title' : label_var.capitalize()},
              'height' : 650}
    
    figure = go.Figure(data = trace, layout = layout)
    return figure