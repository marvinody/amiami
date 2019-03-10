import requests
from bs4 import BeautifulSoup, element
from math import ceil
import re
from urllib.parse import urlencode

rootURL = "https://api.amiami.com/api/v1.0/items"
PER_PAGE = 30
def removeSuffix(str, suffix):
    if str.endswith(suffix):
        return str[: -1*len(suffix)]

class Item:
    def __init__(self, *args, **kwargs):
        self.productURL = kwargs['productURL']
        self.imageURL = kwargs['imageURL']
        self.productName = kwargs['productName']
        self.price = kwargs['price']
        self.productCode = kwargs['productCode']
        self.availability = kwargs['availability']

class ResultSet:

    def __init__(self):
        self.items = []
        self.maxItems = -1
        self.init = False
        self.pages = -1
        self._itemCount = 0

    def add(self, productInfo):
        inStock = productInfo['instock_flg'] == 1
        isClosed = productInfo['order_closed_flg'] == 1
        isPreorder = productInfo['preorderitem'] == 1
        isBackorder = productInfo['list_backorder_available'] == 1
        if isClosed:
            if isPreorder:
                availability = "Pre-order Closed"
            elif isBackorder:
                availability = "Back-order Closed"
            else:
                availability = "Order Closed"
        elif isBackorder:
            availability = "Back-order"
        else:
            if isPreorder and inStock:
                availability = "Pre-order"
            elif inStock:
                availability = "Available"
        item = Item(
            productURL="https://www.amiami.com/eng/detail/?gcode={}".format(productInfo['gcode']),
            imageURL="https://img.amiami.com{}".format(productInfo['thumb_url']),
            productName=productInfo['gname'],
            price=productInfo['c_price_taxed'],
            productCode=productInfo['gcode'],
            availability=availability,
        )
        self.items.append(item)

    def parse(self, obj):
        # returns true when done
        # false if can be called again
        if not self.init:
            self.maxItems = obj['search_result']['total_results']
            self.pages = int(ceil(self.maxItems / float(PER_PAGE)))
            self.init = True
        for productInfo in obj['items']:
            self.add(productInfo)
            self._itemCount += 1

        return self._itemCount == self.maxItems

def search(keywords: str) -> ResultSet:
    data = {
        "s_keywords": keywords,
        "pagecnt": 1,
        "pagemax": PER_PAGE,
        "lang": "eng",
    }
    headers = {
        "X-User-Key": "amiami_dev"
    }
    rs = ResultSet()
    while not rs.parse(requests.get(rootURL, data, headers=headers).json()):
        data['pagecnt'] += 1

    return rs
