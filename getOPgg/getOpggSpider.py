# -*- coding: utf-8 -*-
"""
@author: zh
"""

import json,os,re,time
from datetime import datetime
import requests
from requests.exceptions import RequestException
from multiprocessing import Pool
import pandas

t = str(datetime.now().date()).replace("-","")#当日日期，用来区分不同日期数据

#伪装代理
headers={
    "User-Agent":
             "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36\ (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
    "Referer"
         :"http://www.op.gg/ranking/ladder/"}

def html_parse(url):
    '''
    :param url: http://www.op.gg/ranking/ladder/page=num, 0<=num<=5
    :return: return response from the url if it includes no RuquestException.
    '''
    try:
        htmlpage = requests.get(url,headers=headers)
        if htmlpage.status_code==200:
            return htmlpage.text
    except RequestException as e:
        print(e)
        return None

def get_firtpage(url):
    '''
    :param url: http://www.op.gg/ranking/ladder/page=num, 0<=num<=5
    :return: return a iterable dict which includes data
    '''

    pageContent = html_parse(url)

    pattern_1 = re.compile(
            r'.*?<div class="ranking-highest__rank">(.*?)</div>.*?'
            r'<div class="ranking-highest__icon">.*?</div>.*?'
            r'<a href="(.*?)" class="ranking-highest__name">(.*?)</a>.*?'
            r'<img src=".*?" alt="">.*?'
            r'<span>(.*?)</span>.*?'
            r'<b>(.*?)</b>.*?'
            r'<div class="ranking-highest__level">(.*?)</div>.*?'
            r'<div class="winratio-graph__text winratio-graph__text--left">(.*?)</div>.*?'
            r'<div class="winratio-graph__text winratio-graph__text--right">(.*?)</div>.*?'
            r'<span class="winratio__text">(.*?)</span>.*?'
            , re.M)

    its = re.findall(pattern_1, pageContent)

    if its:
        for it in its:
            yield {
                "rank": it[0],
                "info_href": it[1],
                "name": it[2],
                "segment": it[3],
                "LP": it[4],
                "LV": it[5],
                "win_n": it[6],
                "lose_n": it[7],
                "win_rate": it[8]
            }

    pattern_2 = re.compile(
        r'.*?<tr class="ranking-table__row " id="summoner-\d+">.*?'
        r'<td class="ranking-table__cell ranking-table__cell--rank">(.*?)</td>.*?'
        r'<td class="ranking-table__cell ranking-table__cell--summoner">.*?'
        r'<a href="(.*?)">.*?<img src=".*?" onerror=".*?">.*?'
        r'<span>(.*?)</span>.*?</a>.*?</td>.*?'
        r'<td class="ranking-table__cell ranking-table__cell--tier">(.*?)</td>.*?'
        r'<td class="ranking-table__cell ranking-table__cell--lp">(.*?)</td>.*?'
        r'<td class="ranking-table__cell ranking-table__cell--level">(.*?)</td>.*?'
        r'<td class="ranking-table__cell ranking-table__cell--winratio">.*?'
        r'<div class="winratio-graph">.*?'
        r'<div class="winratio-graph__text winratio-graph__text--left">(.*?)</div>.*?'
        r'<div class="winratio-graph__text winratio-graph__text--right">(.*?)</div>.*?'
        r'<span class="winratio__text">(.*?)</span>.*?</tr>.*?'
        , re.S)

    item = re.findall(pattern_2, pageContent)

    for it in item:
        time.sleep(1)
        yield {
            "rank": it[0],
            "info_href": it[1],
            "name": it[2],
            "segment": it[3].strip(),
            "LP": it[4].strip(),
            "LV": it[5].strip(),
            "win_n": it[6],
            "lose_n": it[7],
            "win_rate": it[8]
        }

def saved_as_json(item):
    '''
    :param item: a dict-like data from the function :get_firtpage
    :return: no ruturns,it writes a json files to save data
    '''

    with open("hanfu_rank_500_%s.txt"%t, "a+",encoding="utf-8") as f:
        f.write(json.dumps(item,ensure_ascii=False)+"\n")
        print("saved a item:", item)

def main(num):
    '''
    :param num: pages of urls which user gives
    :return: no returns but call the function(saved_as_json)
    '''
    url="http://www.op.gg/ranking/ladder/page=%s"%num
    print("load urls:",url)
    for item in get_firtpage(url):
        saved_as_json(item)


if __name__ == '__main__':

    with Pool(5) as pool:
        pool.map(main,range(1,6))






