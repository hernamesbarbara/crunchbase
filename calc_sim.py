#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""calc_sim.py
"""
import os
import sys
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

df = pd.read_csv('deal_details_list.csv')

dfsub = df[df.deal_id.isin(df.deal_id.value_counts()[df.deal_id.value_counts() > 1].index)] # get rid of deals that just have 1 investor
df_wide = pd.pivot_table(dfsub, values=["n"], rows=["financial_organization_name", "deal_id"], aggfunc=np.mean, fill_value=0).unstack()
df_wide = df_wide.fillna(0)


dists = cosine_similarity(df_wide)
dists = pd.DataFrame(dists, columns=df_wide.index)
dists.index = dists.columns

dists["RRE Ventures"].order(ascending=False).head(10)

companies = df[['company_name', 'company_permalink']]

companies = companies.rename(columns={"company_name": "name", "company_permalink": "permalink"})







