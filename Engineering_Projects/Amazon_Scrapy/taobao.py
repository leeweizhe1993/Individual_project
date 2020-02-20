# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import requests as rq
import re
import bs4
from bs4 import BeautifulSoup

def get_text(u):
    try:  
        r = rq.get(u,timeout=30)
        r.raise_for_status
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return ''

    
def parsePage(ilt,html):
    try:
        plt = re.findall(r'\"view_price\"\:\"[\d\.]*\"',html)
        tlt = re.findall(r'\"raw_title\"\:\".*?\"',html)
        for i in range(len(plt)):
            price = eval(plt[i].split(':')[1])
            title = eval(tlt[i].split(':')[1])
            ilt.append([price,title])
    except:
        print('') 

         
def print_goods(ilt):
    tplt = '{:4}\t{:8}\t{:16}'
    print(tplt.format('序号','价格','品名'))
    count = 0
    for g in ilt:
        count = count + 1
        print(tplt.format(count,g[0],g[1]))
    
    
def main():
    goods = '代练'
    depth = 5
    start_u = 'https://s.taobao.com/search?q=' + goods
    infoList = []
    for i in range(depth):
        try:
            u = start_u + '&s=' + str(44*i)
            html = get_text(u)
            parsePage(infoList,html)
        except:
            continue
    print_goods(infoList)
        
main()