# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：    load_biquke.py
   Description：
-------------------------------------------------
__author__ = 'ZH'
"""
from requests import RequestException
from bs4 import BeautifulSoup
import re,os
import requests
import logging
import sys
import MainLoggerConfig
from multiprocessing import Pool
import time
sys.setrecursionlimit(1000000)#防止迭代超过上限报错

MainLoggerConfig.setup_logging(default_path="./logs/logs.yaml")
logging.getLogger("urllib3.connectionpool").setLevel(logging.INFO)

class load_biquge(object):

    logger = logging.getLogger(__name__)

    def __init__(self,mother_url):

        self.mother_url=mother_url#文章链接
        self.path = "./data/{}". \
            format(self.html_parse(self.mother_url).find("h1").string)
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def html_parse(self,url):
        '''
        解析网页返回beautifulsoap对象
        :param url: url
        :return: beautifulsoap对象
        '''
        headers={"user-agent":"Mozilla/5.0 (Windows NT 6.1) "
                              "AppleWebKit/537.36 (KHTML, like Gecko)"
                              " Chrome/63.0.3239.132 Safari/537.36"}
        try:
            content=requests.get(url,headers=headers).content.decode("gbk")
        except RequestException as e:
            self.logger.error("RequestException:",e.args)
            return None
        return BeautifulSoup(content, "html.parser")

    def get_one_page(self,page_url):
        '''
        获取一个章节链接，保存为txt文件
        :param page_url: 章节链接
        :return:
        '''
        text=[]
        self.logger.debug("load a page_url:%s"%page_url)
        time.sleep(1)
        page_content=self.html_parse(page_url)
        title = re.compile(r"\*").sub("", page_content.find("h1").string).strip()
        txt_content=page_content.find("div",id="content").stripped_strings
        for i in txt_content:
            if re.search(r"52bqg\.com",i):
                continue
            text.append(i)
        else:
            with open(os.path.join(self.path,title+".txt"),
                      "w+",encoding="utf-8") as f:
                f.write("\n".join(text))
            self.logger.debug("Successfully downloaded a file:%s.txt" % title)

    def get_page_url(self):
        '''
        解析目标小说链接，返回章节链接
        :return: 返回章节链接
        '''
        mode_page=self.html_parse(self.mother_url)
        ddList = mode_page.find_all("dd")
        return [dd.find("a").get("href") for dd in ddList if dd.find("a")]

if "__main__"==__name__:

    m = load_biquge("https://www.biquge5200.cc/84_84332/")

    try:
        with Pool(5) as pool:
            pool.map(func=m.get_one_page, iterable=m.get_page_url())
    except Exception as e:
        m.logger.error("Pool Err:",e.args)









