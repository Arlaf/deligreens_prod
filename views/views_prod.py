#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 10:10:35 2018

@author: arnaud
"""

import dash_core_components as dcc
import dash_html_components as html
import datetime

def generate_html():
    # Layout
    layout = html.Div([
        html.H1('Hello World !'),
        html.Button(id = 'button1', n_clicks = 0, children = 'Valider'),
        html.Div(id = 'output')
    ])
    
    return layout