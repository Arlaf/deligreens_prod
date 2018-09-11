#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 10:10:35 2018

@author: arnaud
"""

import dash_core_components as dcc
import dash_html_components as html
import datetime
import utilitaires as util

def generate_html():
    
    months_ago = util.AddMonths(util.ajd, -3)
    
    # Layout
    layout = html.Div([
        html.H1('Analyse des ventes par produit'),
        html.Div([
            html.Label('Etudier les ventes entre'),
            dcc.DatePickerRange(
                id = 'date_import_orders',
                display_format = 'DD/MM/YY',
                # start_date par défaut : il y a 3 mois (1er jour du mois)
                start_date = datetime.date(months_ago.year, months_ago.month, 1),
                # end_date par défaut : aujourd'hui
                end_date = util.ajd
            ),
            html.Button(id = 'import_button', n_clicks = 0, children = 'Réimporter', style = {'margin' : '0px 0px 0px 10px'}),
        ], className = 'row'),
        dcc.Checklist(
            id = 'box_rm',
            options = [{'label' : 'Ignorer les commandes des teammates', 'value' : 'rm_teammates'},
                       {'label' : 'Ignorer le product type Frais Livraison', 'value' : 'rm_delivery'}],
            values = ['rm_delivery'],
            style = {'margin' : '10px 0px 0px 0px'}
        ),
        html.Div([
            html.Div([
                html.Label('Sélection des collections'),
                html.Div(id = 'collections_clecklist')
            ], className = 'six columns'),
            html.Div([
                html.Label('Choix de la mesure à afficher'),
                dcc.Dropdown(
                    id = 'dropdown_variable',
                    clearable = False,
                    options = [{'label' : 'Ventes HT', 'value' : 'sells'},
                               {'label' : 'Marge brute', 'value' : 'margin'},
                               {'label' : 'Nombre de produits vendus', 'value' : 'products_sold'}],
                    value = 'sells'),
                dcc.Checklist(
                    id = 'box_pct',
                    options = [{'label' : 'Afficher en pourcentages', 'value' : 'pct'}],
                    values = [],
                    style = {'margin' : '10px 0px 0px 0px'}
                ),
            ], className = 'two columns'),
            html.Div([
                html.Label('Regrouper les produits par'),
                dcc.RadioItems(
                    id = 'radio_level',
                    options=[{'label': 'Collections', 'value': 'collections'},
                             {'label': 'Product types', 'value': 'product_type'}],
                    value='collections')
            ], className = 'two columns'),
            html.Div([
                html.Label('Afficher les résultats par'),
                dcc.RadioItems(
                    id = 'radio_duration',
                    options=[{'label': 'Jours', 'value': 'day'},
                             {'label': 'Semaines', 'value': 'week'},
                             {'label': 'Mois', 'value': 'month'}],
                    value='month')
            ], className = 'two columns')
        ], className = 'row', style = {'margin' : '10px 0px 0px 0px'}),

        dcc.Graph(id = 'graph_sells_evolution'),
        
        # Divs invisibles qui stockeront les données intermédiaires
        html.Div(id = 'df_orders_init_storage', style = {'display': 'none'}),
#        html.Div(id = 'collections_storage', style = {'display': 'none'}),
        html.Div(id = 'df_orders_storage', style = {'display': 'none'})
    ])
    
    return layout