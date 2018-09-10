#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 14:14:54 2018

@author: arnaud
"""
import pandas as pd
import fonctions_api_spfy as fapi
import dash_core_components as dcc

class CollectionsClass:
    
    def __init__(self):
        self.df_collections = pd.read_csv('data/collections_list.csv')
        
        # création d'un df qui contient tous les id produits de toutes les collections
        self.df_col_prod = pd.DataFrame(columns = ['id_col', 'id_prod'])
        for id_col in self.df_collections['Id']:
            temp = pd.DataFrame(columns = ['id_col', 'id_prod'])
            temp['id_prod'] = fapi.get_product_list(id_col)
            temp['id_col'] = id_col
            self.df_col_prod = pd.concat([self.df_col_prod, temp], sort=False)
        
        # Transformation du df pour qu'il n'y ait plus qu'une ligne par produit
        self.df_col_prod = self.df_col_prod.groupby('id_prod').apply(self.product_agg).reset_index()
        
        # Eclatement de la colonne id_col pour qu'il y ait une colonne par collection pour les produits qui en ont plusieurs
        # Et ajout des titres et taxes des collections
        self.ncol_max = self.df_col_prod['ncol'].max()
        for i in range(self.ncol_max):
            # Puisqu'il est impossible de garder le type integer dans une colonne qui contient des valeurs manquantes (car NaN est un float), on utilise des 0 à la place des NaN
            col = 'id_col' + str(i)
            self.df_col_prod[col] = [x[i] if len(x) > i else 0 for x in self.df_col_prod['collections']]
            # Ajout des titres et taxes des collection
            self.df_col_prod = pd.merge(self.df_col_prod, self.df_collections.rename({'Id' : col}, axis='columns'), on=col, how='left').rename({'Title' : 'title'+str(i),
                                                                                                                                                'Handle' : 'handle'+str(i),
                                                                                                                                                'Taux TVA' : 'tva'+str(i)}, axis='columns')

    def product_agg(self, group):
        collections = group['id_col'].tolist()
        n = len(collections)
        column = ['collections','ncol']
        return pd.Series([collections, n], index = column)
    
    def create_collections_dropdown(self):
        options = []
        for col in range(len(self.df_collections)):
            temp = {'label' : self.df_collections['Title'][col],
                    'value' : self.df_collections['Id'][col]}
            options += [temp]
        return dcc.Dropdown(id = 'dropdown_collections',
                            options = options,
                            value = self.df_collections['Id'].tolist(),
                            multi = True)