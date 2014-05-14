#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""fetch_vc_details.py
"""
import pandas as pd
import sys
import os
from crunchbase import Crunchbase
import ujson as json
from pymongo import MongoClient
from datetime import datetime
from operator import itemgetter

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
MONGO_CLIENT = MongoClient(MONGO_URI)

LOG_FORMAT = "{TIMESTAMP}: {MSG}"

def log_msg(msg):
    timestamp = datetime.utcnow()
    return LOG_FORMAT.format(TIMESTAMP=timestamp, MSG=msg)

def save_to_mongo(doc, collection):
    try:
        collection.save(doc)
        return True
    except:
        return False

def new_record(data, entity_type):
    if 'permalink' not in data:
        return None
    if not any(ch.isalpha() for ch in data['permalink']):
        return None
    doc = {'type': 'permalink', 'data': {
        'permalink': data['permalink'], 
        'created_at': datetime.utcnow().isoformat(),
        'entity_type': entity_type}
    }
    return doc


db = MONGO_CLIENT['yhat']
crunchbase = db.crunchbase
seen_permalinks = crunchbase.find({"type": "entity"}).distinct("data.permalink")
seen_permalinks = set(seen_permalinks)

db = MONGO_CLIENT['yhat']
api = Crunchbase(os.environ['CRUNCHBASE_APIKEY'])

companies = [new_record(doc, 'company') for doc in api.all_companies()]
financial_orgs = [new_record(doc, 'financial_organization') for doc in api.all_financial_orgs()]
records = [doc for doc in financial_orgs + companies if doc is not None]

counter = 0
total = len(seen_permalinks)
successful = 0

fmt = "{} of {}"
for doc in records:
    counter += 1
    print log_msg(fmt.format(counter, total))
    if doc['data']['permalink'] not in seen_permalinks:
        successful += save_to_mongo(doc, crunchbase)
    if counter % 10 == 0:
        print log_msg("Saved: {:.0%}".format(successful / float(counter)))
    







