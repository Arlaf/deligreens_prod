#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 14:17:51 2018

@author: arnaud
"""

import requests
import math
import os
#import time

def get_product_list(id_col):
    """Input : l'ID d'une collection
    Output : une liste contenant les ID des produits qui en font partie"""
    
    credentials = {
        'apikey': os.environ.get('apikey'),
        'apisecret': os.environ.get('apisecret')}
    auth = (credentials['apikey'], credentials['apisecret'])
    
#    start_time = time.time()
    # Récupération du nombre de produits de la collection
    r = requests.get('https://courtcircuit.myshopify.com/admin/collects/count.json?collection_id=' + str(id_col), auth = auth)
    print(r.json())
    nprod = r.json()['count']
#    print('Requete COUNT : ' + str(round(time.time() - start_time,3)))
    
    # 250 produits max par page, comptage du nombre d'itérations nécessaires
    N = math.ceil(nprod/250)
    
    products = []
    
    for i in range(1,N+1):
        req = f"""https://courtcircuit.myshopify.com/admin/collects.json?collection_id={id_col}&page={i}&limit=250"""
#        start_time = time.time()
        r = requests.get(req, auth = auth)
#        print('Requete PRODUITS : ' + str(round(time.time() - start_time,3)))
#        start_time = time.time()
        temp = [r.json()['collects'][x]['product_id'] for x in range(len(r.json()['collects']))]
#        print('PARSING : ' + str(round(time.time() - start_time,3)))
#        start_time = time.time()
        products += temp
#        print('CONCATENATION : ' + str(round(time.time() - start_time,3)))
    
    return products