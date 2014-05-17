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

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/crunchbase')
db = MongoClient(MONGO_URI)['yhat']



rm_weird = lambda txt: "".join(ch for ch in txt if ch in string.printable)

if os.path.exists('deal_details_list.csv'):
    print "Already have `deal_details_list.csv` done. Skipping that."
    deal_details = pd.read_csv('deal_details_list.csv')
else:
    print "creating `deal_details_list.csv`"
    
    deal_details_list = []
    counter = 0
    total = db.crunchbase.find({"data.entity_type": "financial_organization"}).count()

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

    deal_details = pd.DataFrame(deal_details_list)
    deal_details.to_csv('deal_details_list.csv', index=False, encoding='utf-8')

if os.path.exists('company_details_list.csv'):
    print "Already have `company_details_list.csv` done. Skipping that."
    company_details = pd.read_csv('company_details_list.csv')
else:
    print "creating `company_details_list.csv`"
    
    company_details_list = []
    total = db.crunchbase.find({"data.entity_type": "company"}).count()
    counter = 0
    for doc in db.crunchbase.find({"data.entity_type": "company"}).batch_size(100):
        counter += 1
        if counter % 1000 == 0:
            print "{} of {}".format(counter, total)

        funding_rounds = []
        company_permalink = doc['data']['permalink']
        company_name = doc['data']['name']
        company_n_funding_rounds = len(doc['data']['funding_rounds'])
        
        for deal in doc['data']['funding_rounds']:
            participants = []
            day,month,year = deal['funded_day'],deal['funded_month'],deal['funded_year']
            crunchbase_round_id = str(deal['id'])
            deal_round = deal['round_code']
            deal_raised_amt = deal['raised_amount']
            deal_currency_code = deal['raised_currency_code']
            for investment in deal['investments']:
                if investment.get('company'):
                    name = investment['company']['name']
                    permalink = investment['company']['permalink']
                    participants.append(['company', name, permalink])
                if investment.get('person'):
                    first, last = investment['person']['first_name'], investment['person']['last_name']
                    full_name = first + ' ' + last
                    permalink = investment['person']['permalink']
                    participants.append(['person', full_name, permalink])
                if investment.get('financial_org'):
                    name = investment['financial_org']['name']
                    permalink = investment['financial_org']['permalink']
                    participants.append(['financial_org', name, permalink])

            for participant in participants:
                record = {
                    "company_name": company_name, 
                    "company_permalink": company_permalink,
                    "company_n_funding_rounds": company_n_funding_rounds,
                    "deal_funded_day": day,
                    "deal_funded_month": month,
                    "deal_funded_year": year,
                    "crunchbase_round_id": crunchbase_round_id,
                    "deal_round": deal_round,
                    "deal_raised_amount": deal_raised_amt,
                    "deal_currency_code": deal_currency_code,
                    "participant_type": participant[0],
                    "participant_name": participant[1],
                    "participant_permalink": participant[2]
                }
                funding_rounds.append(record)
        
        if funding_rounds:
            for rnd in funding_rounds:
                company_details_list.append(rnd)
        else:
            record = {
                "company_name": company_name, 
                "company_permalink": company_permalink,
                "company_n_funding_rounds": 0,
                "deal_funded_day":None,
                "deal_funded_month":None,
                "deal_funded_year":None,
                "crunchbase_round_id":None,
                "deal_round":None,
                "deal_raised_amount":None,
                "deal_currency_code":None,
                "participant_type":None,
                "participant_name":None,
                "participant_permalink":None
            }
            company_details_list.append(record)

    company_details = pd.DataFrame(company_details_list)
    company_details.to_csv("company_details_list.csv", index=False, encoding="utf-8")






