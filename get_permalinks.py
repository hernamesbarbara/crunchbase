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
import datetime
from operator import itemgetter

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
MONGO_CLIENT = MongoClient(MONGO_URI)

def save_to_mongo(documents, database):
    try:
        return database['permalinks'].insert(documents)
    except:
        return False

def new_record(data, entity_type):
    if 'permalink' not in data:
        return None
    if not any(ch.isalpha() for ch in data['permalink']):
        return None
    doc = {
        'permalink': data['permalink'], 
        'created_at': datetime.datetime.utcnow().isoformat(),
        'entity_type': entity_type
    }
    return doc


def main():
    db = MONGO_CLIENT['crunchbase']
    api = Crunchbase(os.environ['CRUNCHBASE_APIKEY'])
    fmt = """{}\nFetched: {}\nSaved: {}"""
    companies = [new_record(doc, 'company') for doc in api.all_companies()]
    financial_orgs = [new_record(doc, 'financial_organization') for doc in api.all_financial_orgs()]
    print "Fetched {} companies and financial orgs".format(len(companies+financial_orgs))
    companies = [doc for doc in companies if doc is not None]
    financial_orgs = [doc for doc in financial_orgs if doc is not None]
    records = financial_orgs + companies
    records = sorted(records, key=itemgetter('entity_type', 'permalink'))
    print "Trying to save {} non-null records to mongodb.".format(len(records))
    record_ids = save_to_mongo(records, db)
    print "Successfully Saved {} permalink records".format(len(record_ids))


if __name__ == '__main__':
    main()




