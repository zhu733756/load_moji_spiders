# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     load_www_lxf.py
   Description：
-------------------------------------------------
__author__ = 'ZH'
"""

import requests
from bs4 import BeautifulSoup
import re
from multiprocessing import Pool, freeze_support
from multiprocessing.dummy import Pool
import random
import os

# 用户代理列表
agents = [
    "Mozilla/5.0 (Linux; U; Android 2.3.6; en-us; Nexus S Build/GRK39F) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Avant Browser/1.2.789rel1 (http://www.avantbrowser.com)",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.5 (KHTML, like Gecko) Chrome/4.0.249.0 Safari/532.5",
    "Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/532.9 (KHTML, like Gecko) Chrome/5.0.310.0 Safari/532.9",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.514.0 Safari/534.7",
    "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/9.0.601.0 Safari/534.14",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/10.0.601.0 Safari/534.14",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.20 (KHTML, like Gecko) Chrome/11.0.672.2 Safari/534.20",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.27 (KHTML, like Gecko) Chrome/12.0.712.0 Safari/534.27",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.24 Safari/535.1",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.120 Safari/535.2",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.36 Safari/535.7",
    "Mozilla/5.0 (Windows; U; Windows NT 6.0 x64; en-US; rv:1.9pre) Gecko/2008072421 Minefield/3.0.2pre",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.10) Gecko/2009042316 Firefox/3.0.10",
    "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-GB; rv:1.9.0.11) Gecko/2009060215 Firefox/3.0.11 (.NET CLR 3.5.30729)",
    "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6 GTB5",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; tr; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8 ( .NET CLR 3.5.30729; .NET4.0E)",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0a2) Gecko/20110622 Firefox/6.0a2",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:7.0.1) Gecko/20100101 Firefox/7.0.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0b4pre) Gecko/20100815 Minefield/4.0b4pre",
    "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.0 )",
    "Mozilla/4.0 (compatible; MSIE 5.5; Windows 98; Win 9x 4.90)",
    "Mozilla/5.0 (Windows; U; Windows XP) Gecko MultiZilla/1.6.1.0a",
    "Mozilla/2.02E (Win95; U)",
    "Mozilla/3.01Gold (Win95; I)",
    "Mozilla/4.8 [en] (Windows NT 5.1; U)",
    "Mozilla/5.0 (Windows; U; Win98; en-US; rv:1.4) Gecko Netscape/7.1 (ax)"
]


def html_response(url):
    '''
    给定url，返回网页数据，如果ip被禁止，则返回一个状态码
    :param url:
    :return:
    '''
    headers = {
        "User-Agent": random.choice(agents)
    }
    page_content = requests.get(url=url, headers=headers)
    if page_content:
        return BeautifulSoup(page_content.text, "html.parser")
    else:
        return page_content.raise_for_status()


def get_text(son_url):
    '''
    返回一个网页文件的列表text
    :param son_url:
    :return:
    '''
    print("load son_url:", son_url)

    div_list = html_response(son_url).find("div", "x-content")
    parent = div_list.find("div", "x-wiki-content")

    text = []

    for child in parent:
        try:
            free_text = "".join(child.strings)#获取文本
        except:
            free_text = ""
        try:
            try:
                string = child.find(src=True).get("src")#获取图片
            except:
                string = child.find(href=True).get("href")#如果没有图片，就获取链接
        except:
            pass
        else:
            if string:
                free_text = "\n".join([free_text, string])
        finally:
            text.append(free_text)
    else:
        return text


def save_file(content, title, dir):
    '''
    保存网页数据到指定路径
    :param content:
    :param title:
    :param dir:
    :return:
    '''

    with open(dir + title + ".txt", "w") as f:
        f.write(content)
        print("a title(%s) was done!" % title)


def main(number, dir):
    '''
    启动函数，用多进程爬取网页
    :param number:
    :param dir:
    :return:
    '''

    base_url = "https://www.liaoxuefeng.com"
    mother_url = "".join([base_url, "/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000"])

    try:
        mode_html = html_response(mother_url)
        mode_content = mode_html.find("ul", id="x-wiki-index")
        a_list = mode_content.find_all("a")
    except Exception as e:
        print(e)

    with Pool(4) as pool:
        try:
            for num, a in enumerate(a_list):
                if num < number:
                    continue
                son_url = base_url + a.get("href")
                title = "".join([str(num), a.string])
                content = "".join(get_text(son_url))
                pool.apply_async(func=save_file, args=(content, title, dir))
        except Exception as e:
            print("pool err:", e)
    pool.close()
    pool.join()
    print("all done!")


if __name__ == '__main__':
    freeze_support()
    maxnumber = []
    dir = "./data/"
    if not os.path.exists(dir):
        os.mkdir(dir)
    try:
        for filename in os.listdir(dir):
            maxnumber.append(int(re.search(r"\d+", filename).group()))
        else:
            number = max(maxnumber)
            main(number, dir)
    except:
        main(0,dir)

    
