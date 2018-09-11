#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 10:12:02 2018

@author: arnaud
"""
import fonctions_core_bd as fcore
from models import mod_collections
import utilitaires as util
import datetime
import pandas as pd

class OrdersClass:
    
    def __init__(self):
        self.collections = mod_collections.CollectionsClass()
        
    def get_data(self, date):
        req = f"""SELECT o.order_number,
                    o.created_at,
                    o.financial_status,
                    o.total_price_cents,
                    o.total_discounts_cents,
                    o.total_tax_cents,
                    o.total_shipping_cents,
                    o.total_refund_cents,
                    li.variant_id,
                    li.quantity,
                    li.buying_price_cents AS buying_price_cent_ht,
                    li.selling_price_cents AS selling_price_cent_ttc,
                    li.pre_tax_price_cents AS selling_price_cent_ht,
                    li.tax_amount_cents,
                    li.tax_rate,
                    v.sku,
                    p.shopify_id AS id_prod,
                    p.title,
                    p.product_type,
                    p.handle,
                    o.client_id,
                    c.email
                FROM line_items li, orders o, variants v, products p, clients c
                WHERE o.id = li.order_id and li.variant_id = v.id and v.product_id = p.id and o.client_id = c.id and o.created_at >=  '{str(date)}'"""
                
        # Extraction des self.commandes de Core
        df_orders = fcore.extract_core(req)
        
        # On n'a pas besoin de l'heure, on va juste garder les dates
        df_orders['created_at'] = df_orders['created_at'].dt.date
        
        # On retire les self.commandes refunded ou voided
        df_orders = df_orders.loc[~df_orders.financial_status.isin(['refunded','voided'])]
        
        # On a plus besoin de financial_status
        df_orders = df_orders.drop('financial_status', axis=1)
        
        # Ajout des collections des produits
        df_orders = pd.merge(df_orders, self.collections.df_col_prod, on="id_prod", how="left")
        
        # Ajout de la colonne semaine (qui contient en fait la date du lundi de la semaine en question)
        df_orders['week'] = [d - datetime.timedelta(days=d.weekday()) for d in df_orders['created_at']]
        
        # Ajout de la colonne mois (qui contient en fait la date 1er jour du mois)
        df_orders['month'] = [datetime.date(d.year, d.month, 1) for d in df_orders['created_at']]
        
        return df_orders
        
    def filtrage(self, df_orders_json, rm, start, end):
        
        df_orders = pd.read_json(df_orders_json, orient = 'split', convert_dates = ['created_at'])
        
        if 'rm_teammates' in rm:
            # Liste des équipiers
            teammates = ['dumontet.thibaut@gmail.com', 'dumontet.julie@gmail.com', 'laura.h.jalbert@gmail.com', 'rehmvincent@gmail.com', 'a.mechkar@gmail.com', 'helena.luber@gmail.com', 'martin.plancquaert@gmail.com', 'badieresoscar@gmail.com', 'steffina.tagoreraj@gmail.com', 'perono.jeremy@gmail.com', 'roger.virgil@gmail.com', 'boutiermorgane@gmail.com', 'idabmat@gmail.com', 'nadinelhubert@gmail.com', 'faure.remi@yahoo.fr', 'maxime.cisilin@gmail.com', 'voto.arthur@gmail.com', 'pedro7569@gmail.com']
            # On retire commandes des équipiers
            df_orders = df_orders.loc[~df_orders.email.isin(teammates)]
        
        if 'rm_delivery' in rm:
            # On retire les product types Frais Livraison
            df_orders = df_orders.loc[df_orders['product_type'] != 'Frais Livraison',:]
            
        # Filtrage par date
        df_orders = df_orders.loc[(df_orders['created_at'] >= pd.Timestamp(start)) & (df_orders['created_at'] <= pd.Timestamp(end)),:].copy()
        
        return df_orders