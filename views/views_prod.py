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
            id = 'box_rm_teammates',
            options = [{'label' : 'Ignorer les commandes des teammates', 'value' : 'rm_teammates'}],
            values = [],
            style = {'margin' : '10px 0px 0px 0px'}
        ),
        html.Label('Sélection des collections', style = {'margin' : '10px 0px 0px 0px'}),
        html.Div(id = 'collections_clecklist'),
        
        dcc.Graph(id = 'graph_sells_evolution'),
        
        # Divs invisibles qui stockeront les données intermédiaires
        html.Div(id = 'df_orders_init_storage', style = {'display': 'none'}),
#        html.Div(id = 'collections_storage', style = {'display': 'none'}),
        html.Div(id = 'df_orders_storage', style = {'display': 'none'})
    ])
    
    return layout