#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""fetchall_details.py
"""
import pandas as pd
import sys
import os
from crunchbase import Crunchbase
import ujson as json
from operator import itemgetter
import csv

def setup_api():
    try:
        api = Crunchbase(os.environ['CRUNCHBASE_APIKEY'])
    except:
        api = None
    return api

def read_and_sort_json(filename):
    f = open(filename)
    return sorted(json.load(f), key=itemgetter('permalink'))

def is_new(name, entity_type):
    fmt = "./data/{entity_type}/{name}.json"
    fullpath = fmt.format(entity_type=entity_type, name=name)
    return not os.path.exists(fullpath)

def get_permalinks(entity_type):
    entity_filename = "./data/{entity_type}.json".format(entity_type=entity_type)
    for dct in read_and_sort_json(entity_filename):
        if is_new(dct['permalink'], entity_type):
            yield dct['permalink']

def save_to_file(data, dirname, permalink):
    fmt = "./data/{dirname}/{permalink}.json"
    outfile = fmt.format(dirname=dirname, permalink=permalink)
    with open(outfile, 'wb') as f:
        json.dump(data, f)


if os.path.exists("info.log"):
    loginfo = open('info.log', 'a')
else:
    loginfo = open('info.log', 'wb')

if os.path.exists("fetchall_details.log.csv"):
    logcsv = open('fetchall_details.log.csv', 'a')
    logwriter = csv.writer(logcsv)
else:
    logcsv = open('fetchall_details.log.csv', 'wb')
    logwriter = csv.writer(logcsv)
    logwriter.writerow(['entity_type', 'permalink', 'success?'])

api = setup_api()

for entity_type in ['financial-organizations', 'companies']:
    loginfo.write("processing {}\n".format(entity_type))
    for i, permalink in enumerate(get_permalinks(entity_type)):
        loginfo.write("permalink #{} => {}\n".format(i, permalink))
        if entity_type == 'companies':
            try:
                res = api.company(permalink)
            except:
                res = None
        else:
            try:
                res = api.financial_org(permalink)
            except:
                res = None
        if res is None:
            logwriter.writerow([entity_type, permalink, False])
            save_to_file({"permalink": permalink}, entity_type, permalink)
        else:
            logwriter.writerow([entity_type, permalink, True])
            save_to_file(res, entity_type, permalink)

logcsv.close()
loginfo.close()

