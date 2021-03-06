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

def level_duration_agg(group, level):
    """Agrège df_orders et calcule les mesures pour chaque période et chaque niveau de produit"""
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
    cols = [c1, c2, c3]
    colnames = ['sells', 'margin', 'products_sold']
    if level == 'product_type':
        c4 = group['title0'].reset_index(drop=True)[0]
        cols += [c4]
        colnames += ['title0']
    return pd.Series(cols, index = colnames)

#def tot_agg(group, variable):
#    c1 = group[variable].sum()
#    return pd.Series([c1], index = [variable])
    
def tot_agg(group):
    """Ajoute au df groupé par période les colonnes des totaux et pourcentages de chaque variable"""
    for var in ['sells', 'margin', 'products_sold']:
        res = group[var].sum()
        name_tot = var + '_tot'
        group[name_tot] = res
        name_pct = var + '_pct'
        group[name_pct] = group[var]/group[name_tot]
    return group

def construct_table_evolution(df_orders_json, duration, level):
    df_orders = pd.read_json(df_orders_json, orient = 'split', convert_dates = ['created_at', 'week', 'month'])
    # La lecture du json a passé les id_col en float alors on les reconvertit en string
    df_orders['id_col0'] = [str(x)[:-2] for x in df_orders['id_col0']]
    # La lecture du json a passé les dates en timestamp, on les remet en datetime.date
    for date_col in ['created_at', 'week', 'month']:
        df_orders[date_col] = [datetime.date(d.year, d.month, d.day) for d in pd.to_datetime(df_orders[date_col])]
    
#    # On ne garde que les collections voulues
#    df_orders = df_orders.loc[df_orders['id_col0'].isin(collections), :]
    if level == 'collections':
        level = 'title0'
    # Agregation par niveau et période
    table = df_orders.groupby([duration,level]).apply(level_duration_agg, level).unstack(fill_value = 0).stack().reset_index()
    # Création des colonnes des totaux par périodes et des pourcentages de chaque niveau de produit
    table = table.groupby(duration).apply(tot_agg)
    return table
        
    
def construct_graph_evolution(table_evolution_json, collections, variable, pct, duration, level):
    table = pd.read_json(table_evolution_json, orient = 'split', convert_dates = [duration])
    table[duration] = [datetime.date(d.year, d.month, d.day) for d in pd.to_datetime(table[duration])]
    
    # On ne garde que les collections sélectionnées
    table = table.loc[table['title0'].isin(collections),:]

    if level == 'collections':
        level = 'title0'
    
    trace = []
    for lev in table[level].unique():
        df = table.loc[table[level] == lev, :]
        x = [d.strftime('%B %y').capitalize() if duration == 'month' else d.strftime('%d %B %y') for d in df[duration]]
        y = df[variable+'_pct'] if pct else df[variable]
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

def display_table_evolution(table_evolution_json, collections, variable, pct, duration, level):
    table = pd.read_json(table_evolution_json, orient = 'split', convert_dates = [duration])
    table[duration] = [datetime.date(d.year, d.month, d.day) for d in pd.to_datetime(table[duration])]
    
    # On ne garde que les collections sélectionnées
    table = table.loc[table['title0'].isin(collections),:]

    if level == 'collections':
        name = 'Collection'
        level = 'title0'
    else:
        name = 'Product type'
    table = table.rename({level : name}, axis = 'columns')
        
    if pct:
        variable = variable + '_pct'
        table[variable] = util.format_pct(table[variable])
    else:
        if variable == 'products_sold':
            table[variable] = util.format_entiers(table[variable])
        else:
            table[variable] = util.format_montant(table[variable])
    
    table[duration] = [d.strftime('%B %y').capitalize() if duration == 'month' else d.strftime('%d %B %y') for d in table[duration]]
    
    table = table.pivot(index=name, columns=duration, values=variable).reset_index()
    
    return table
