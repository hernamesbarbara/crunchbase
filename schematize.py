#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""get_details.py
"""
import numpy as np
import pandas as pd
import sys
import os
import string
import json
from pymongo import MongoClient
from datetime import datetime
from crunchbase import Crunchbase

pd.options.display.max_columns = 15
pd.options.display.width = 900

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/crunchbase')
db = MongoClient(MONGO_URI)['yhat']

deal_details_list = []
counter = 0
total = db.crunchbase.find({"data.entity_type": "financial_organization"}).count()

rm_weird = lambda txt: "".join(ch for ch in txt if ch in string.printable)

for doc in db.crunchbase.find({"data.entity_type": "financial_organization"}).batch_size(100):
    counter += 1
    financial_organization_permalink = doc['data']['permalink']
    financial_organization_name = doc['data']['name']
    for deal in doc['data']['investments']:
        details = deal.get('funding_round')
        if details:
            company = details.get('company')
            company_name = company.get('name')
            funded_year = details.get('funded_year')
            funded_month = details.get('funded_month')
            funded_day = details.get('funded_day')
            funded_round = details.get('round_code')
            deal_id_list = ["".join(company_name.split()), str(funded_year), str(funded_month), str(funded_day), funded_round]
            deal_id = "-".join(map(rm_weird, deal_id_list))
            record = {
                "company_name": company.get('name'),
                "company_permalink": company.get('permalink'),
                "financial_organization_name": financial_organization_name,
                "financial_organization_permalink": financial_organization_permalink,
                "deal_funded_day": details.get('funded_day'),
                "deal_funded_month": details.get('funded_month'),
                "deal_funded_year": details.get('funded_year'),
                "deal_amount": details.get('raised_amount'),
                "deal_currency_code": details.get('raised_currency_code'),
                "deal_round": details.get('round_code'),
                "deal_id": deal_id
            }
            deal_details_list.append(record)

    if counter % 100 == 0:
        print "{} of {}".format(counter, total)

df = pd.DataFrame(deal_details_list)
# df.to_csv('deal_details_list.csv', index=False, encoding='utf-8')
dfsub = df[df.deal_id.isin(df.deal_id.value_counts()[df.deal_id.value_counts() > 1].index)] # get rid of deals that just have 1 investor
df_wide = pd.pivot_table(dfsub, values=["n"], rows=["financial_organization_name", "deal_id"], aggfunc=np.mean, fill_value=0).unstack()
df_wide = df_wide.fillna(0)

from sklearn.metrics.pairwise import cosine_similarity
dists = cosine_similarity(df_wide)
dists = pd.DataFrame(dists, columns=df_wide.index)
dists.index = dists.columns

dists["RRE Ventures"].order(ascending=False).head(10)

