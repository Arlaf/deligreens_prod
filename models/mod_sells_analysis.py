#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 10 13:22:05 2018

@author: arnaud
"""

import pandas as pd

def construct_graph_sells_evolution(df_orders_json, collections):
    df_orders = pd.read_json(df_orders_json, orient = 'split', convert_date = ['created_at', 'week', 'month'])
    
    
    return figure