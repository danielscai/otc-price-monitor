#!/usr/bin/python3
#encoding:utf-8

import sys
import logging
import requests 
from lxml import etree

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

r = requests.get("https://otcbtc.com/sell_offers?currency=eth&fiat_currency=cny&payment_type=all",timeout=4)
text = r.content

huobi_request = requests.get('https://otc.huobipro.com/#/trade/list?coin=2&type=1',timeout=4)
huobi_text = huobi_request.content

logger.debug('Done get Html')

class OTCBTC:
    otc_price_xpath = '/html/body/div[2]/div/div/div[1]/div/div[1]/div[2]/div/div[1]/div[1]/div[4]/div[1]'
    market_price_xpath='/html/body/div[2]/div/div/div[2]/div/div[2]/div/span[3]'
    
     
    def render(self, html):
        self.tree = etree.HTML(html)
        #self.market_price = self.get_xpath_value(self.market_price_xpath)
        self.otc_price = self.get_xpath_value(self.otc_price_xpath)
        #self.calc_over_percent()

    def get_xpath_value(self, xpath):
        logger.debug(xpath)
        element = self.tree.xpath(xpath)
        logger.debug(element)
        if len(element) == 0:
            text = element.text
        else:
            text = element[0].text
        return float( text.strip().replace(',','').replace('CNY','').strip())

    def calc_over_percent(self):
        self.over_percent = ((self.otc_price / self.market_price) - 1 ) * 100

class Huobi(OTCBTC):
    otc_price_xpath = '//*[@id="app"]/div[3]/div/div/div[2]/div/div/div[3]/div[1]/div[1]/div[5]/div/p[1]/span'
    market_price_xpath = '//*[@id="app"]/div[1]/div[1]/div/div[3]/span[2]'


venders = []

#otcbtc = OTCBTC()
#otcbtc.render(text)
#
#venders.append(otcbtc)

huobi= Huobi()
huobi.render(huobi_text)
venders.append(huobi)



for i in venders:
    print(u'场外价格:{0}'.format(i.otc_price))
    print(u'场内价格:{0}'.format(i.market_price))
    print(u'溢价率:{0}'.format(i.over_percent))
    
