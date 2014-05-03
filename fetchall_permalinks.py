#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""fetch_vc_details.py
"""
import pandas as pd
import sys
import os
from crunchbase import Crunchbase
from crunchbase import rm_quotes
import ujson as json

def setup_api():
    try:
        api = Crunchbase(os.environ['CRUNCHBASE_APIKEY'])
    except:
        api = None
    return api

def main():
    api = setup_api()
    if api is None:
        print >> sys.stderr, "Unable to authenticate to crunchbase API."
        sys.exit(1)

    if 'financial-organizations.json' not in os.listdir("./data/"):
        try:
            with open('financial-organizations.json', 'wb') as f:
                data = api.all_financial_orgs()
                json.dump(data, f)
        except:
            print >> sys.stderr, "Unable to get financial organizations"
            sys.exit(1)

    if 'companies.json' not in os.listdir("./data/"):
        try:
            with open('companies.json', 'wb') as f:
                data = api.all_companies()
                json.dump(data, f)
        except:
            print >> sys.stderr, "Unable to get companies"
            sys.exit(1)
    for filename in os.listdir("./data/"):
        print >> sys.stdout, "./data/" + filename
    sys.exit(0)

if __name__ == "__main__":
    main()
