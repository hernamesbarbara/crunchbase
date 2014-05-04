#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""get_details.py
"""
import pandas as pd
import sys
import os
from crunchbase import Crunchbase
import ujson as json
from pymongo import MongoClient
import datetime
import time

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/crunchbase')
db = MongoClient(MONGO_URI)['crunchbase']
api = Crunchbase(os.environ['CRUNCHBASE_APIKEY'])



for doc in db.permalinks.find({}):
    if db['entities'].find_one({'permalink': doc['permalink']}):
        continue
    if doc['entity_type'] == 'company':
        details = api.company(doc['permalink'])
    if doc['entity_type'] == 'financial_organization':
        details = api.financial_org(doc['permalink'])
    db['entities'].insert(details)




