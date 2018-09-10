#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  5 18:00:42 2018

@author: arnaud
"""

import os
import dash
import dash_auth


from models import mod_orders

# Pour avoir les mois des dates en français
import locale
locale.setlocale(2,'')

#df_orders = mod_orders.OrdersClass().df_orders

# Déclaration de l'application    
app = dash.Dash('auth')
auth = dash_auth.BasicAuth(app, [[os.environ['appuser'],os.environ['apppass']]])

server = app.server

# Pour éviter les warnings dus au multipage layout
app.config.suppress_callback_exceptions = True

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})