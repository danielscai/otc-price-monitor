#!/usr/bin/python3
#encoding:utf-8

import sys
import logging
import requests 
from lxml import etree

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)


class Vender:
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    def calc_over_percent(self):
        self.over_percent = ((self.otc_price / self.market_price) - 1 ) * 100

class OTCBTC(Vender):
    name='otcbtc'
    currency=None
    
    otc_price_xpath = '/html/body/div[2]/div/div/div[1]/div/div[1]/div[2]/div/div[1]/div[1]/div[4]/div[1]'
    market_price_xpath='/html/body/div[2]/div/div/div[2]/div/div[2]/div/span[3]'

    def __init__(self, currency):
        self.currency = currency 
        self.url = "https://otcbtc.com/sell_offers?currency={0}&fiat_currency=cny&payment_type=all".format(currency)
    
    def get_html(self):
        r = requests.get(self.url,timeout=4,headers=self.headers)
        text = r.content
        self.html = text

    def get_price(self):
        self.render()
     
    def render(self):
        self.get_html()
        self.tree = etree.HTML(self.html)
        self.market_price = self.get_xpath_value(self.market_price_xpath)
        self.otc_price = self.get_xpath_value(self.otc_price_xpath)
        self.calc_over_percent()

    def get_xpath_value(self, xpath):
        logger.debug(xpath)
        element = self.tree.xpath(xpath)
        logger.debug(element)
        if len(element) == 0:
            text = element.text
        else:
            text = element[0].text
        return float( text.strip().replace(',','').replace('CNY','').strip())


class Huobi(Vender):
    name=u'火币'
    market_price_api = 'https://api-otc.huobi.pro/v1/otc/base/market/price'

    def __init__(self,currency):
        self.currency = currency
        if currency == 'usdt':
            self.coin_id = 2
            self.otc_price_api = 'https://api-otc.huobi.pro/v1/otc/trade/list/public?coinId={0}&tradeType=1&currentPage=1&payWay=&country=&merchant=0&online=1&range=0'.format(self.coin_id)


    def get_price(self):
        
        data = self.get_api_json(self.otc_price_api)
        self.otc_price = self.get_min_price(data)

        market_price_data = self.get_api_json(self.market_price_api)
        logger.debug(self.market_price_api)
        self.market_price = self.get_market_price(market_price_data)

        logger.debug(self.otc_price)
        logger.debug(self.market_price)
        self.calc_over_percent()


    def get_api_json(self,url):
        r = requests.get(url,timeout=4,headers=self.headers)
        r_json =  r.json()
        return r_json['data']
        

    def get_min_price(self,data):
        price_all=[]
        for d in data:
            price_all.append(float(d['price']))
        min_price = min(price_all)
        logger.debug(min_price)
        return min_price
        
    def get_market_price(self,data):
        logger.debug('calc market price')
        for d in data:
            if d['coinId'] == self.coin_id:
                return float(d['price'])

        
        
venders = []

otcbtc = OTCBTC('usdt')
otcbtc_eth = OTCBTC('eth')
huobi = Huobi('usdt')

venders.append(otcbtc)
venders.append(otcbtc_eth)
venders.append(huobi)

for v in venders:
    v.get_price()

for v in venders:
    logger.info(u'网站:{0}-{1}'.format(v.name, v.currency))
    print(u'场外价格:{0}'.format(v.otc_price))
    print(u'场内价格:{0}'.format(v.market_price))
    print(u'溢价率:{0}'.format(v.over_percent))
    
