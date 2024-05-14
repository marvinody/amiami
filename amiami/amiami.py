from math import ceil
# import logging
from curl_cffi import requests


rootURL = "https://api.amiami.com/api/v1.0/items"
PER_PAGE = 30

class Item:
    def __init__(self, *args, **kwargs):
        self.productURL = kwargs['productURL']
        self.imageURL = kwargs['imageURL']
        self.productName = kwargs['productName']
        self.price = kwargs['price']
        self.productCode = kwargs['productCode']
        self.availability = kwargs['availability']
        self.flags = kwargs['flags']

class ResultSet:

    def __init__(self):
        self.items = []
        self.maxItems = -1
        self.init = False
        self.pages = -1
        self._itemCount = 0

    def add(self, productInfo):
       
        availability = "Unknown status?"
        isSale = productInfo['saleitem'] == 1
        isLimited = productInfo['list_store_bonus'] == 1 or productInfo['list_amiami_limited'] == 1
        isPreowned = productInfo['condition_flg'] == 1
        isPreorder = productInfo['preorderitem'] == 1
        isBackorder = productInfo['list_backorder_available'] == 1
        isClosed = productInfo['order_closed_flg'] == 1
        
        flags = {
            "isSale": isSale,
            "isLimited": isLimited,
            "isPreowned": isPreowned,
            "isPreorder": isPreorder,
            "isBackorder": isBackorder,
            "isClosed": isClosed,
        }
        if isClosed:
            if isPreorder:
                availability = "Pre-order Closed"
            elif isBackorder:
                availability = "Back-order Closed"
            else:
                availability = "Order Closed"
        else:
            if isPreorder:
                availability = "Pre-order"
            elif isBackorder:
                availability = "Back-order"
            elif isPreowned:
                availability = "Pre-owned"
            elif isLimited:
                availability = "Limited"
            elif isSale:
                availability = "On Sale"
            else:
                availability = "Available"

        if availability == "Unknown status?":
            print("STATUS ERROR FOR {}: flags:{}, avail:{}".format(
                productInfo['gcode'],
                flags,
                availability,
            ))
        item = Item(
            productURL="https://www.amiami.com/eng/detail/?gcode={}".format(productInfo['gcode']),
            imageURL="https://img.amiami.com{}".format(productInfo['thumb_url']),
            productName=productInfo['gname'],
            price=productInfo['c_price_taxed'],
            productCode=productInfo['gcode'],
            availability=availability,
            flags=flags,
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

# leaving this here because I need it every time some shit breaks and don't wanna dig it up
# logging.basicConfig(
#     format="%(levelname)s [%(asctime)s] %(name)s - %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
#     level=logging.DEBUG
# )

def search(keywords):
    data = {
        "s_keywords": keywords,
        "pagecnt": 1,
        "pagemax": PER_PAGE,
        "lang": "eng",
    }
    headers = {
        "X-User-Key": "amiami_dev",
        "User-Agent": "python-amiami_dev",
    }

    rs = ResultSet()
    hasMore = True
    while hasMore:
        resp = requests.get(rootURL, params=data, headers=headers, impersonate="chrome110")
        hasMore = not rs.parse(resp.json())
        data['pagecnt'] += 1

    return rs
