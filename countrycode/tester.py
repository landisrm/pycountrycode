# -*- coding: utf-8 -*-

import countrycode as cc
import pandas as pd
import re


target = 'Sao Tom\xc3\xa9 & Principe'
target = unicode(target, 'utf-8')

rx = cc.data.regex[cc.data.label_name == 'Sao Tome and Principe'].iloc[0]
pat = re.compile(rx)
res = pat.search(target)
if res is not None:
    print res.group(0)

rx1 = rx.encode('utf-8')
pat1 = re.compile(rx1)
res1 = pat.search(target)
if res1 is not None:
    print res1.group(0)
