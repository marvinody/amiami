import requests
from bs4 import BeautifulSoup, element
from math import ceil
class SimpleItem:
    def __init__(self, *args, **kwargs):
        self.productURL = kwargs['productURL']
        self.imageURL = kwargs['imageURL']
        self.productName = kwargs['productName']
        self.price = kwargs['price']

    @staticmethod
    def parse(product_box_soup: element.Tag):
        data = {
            'productURL': product_box_soup.find('a')['href'],
            'imageURL': product_box_soup.find('img')['src'],
            'productName': product_box_soup.find_all('a')[1].text,
            # for some reason, it has a bunch of tabs everywhere for spacing
            'price': product_box_soup.find('li',class_='product_price').text.strip(),

        }
        return SimpleItem(**data)

class Item(SimpleItem):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.availability = kwargs['availability']
        self.brand = kwargs['brand']
        self.productCode = kwargs['productCode']

    @staticmethod
    def use(simpleItem: SimpleItem):
        url = simpleItem.productURL
        data = vars(simpleItem)
        soup = BeautifulSoup(requests.get(url).text, 'html5lib')
        right_menu = soup.find(id="right_menu")
        inputs = right_menu.find_all('input')
        data['productCode'] = inputs[0]['value']
        if len(inputs) == 3:
            data['availability'] = inputs[2]['alt']
        else:
            avail = right_menu.find('span').find('img')['alt']
            if avail != u'OrdersClosed':
                raise Exception("NEW UNSEEN AVAILABILITY DETECTED: {}".format(avail))
            data['availability'] = avail
        # find the brand title, go up, go 2 next, and get the text
        data['brand'] = right_menu.find(string='Brand').parent.next_sibling.next_sibling.find('a').text
        data['productCode'] = right_menu.find(string='Item Code').parent.next_sibling.next_sibling.text
        return Item(**data)


class ResultSet:

    def __init__(self):
        self.items = []
        self.maxItems = -1
        self.init = False
        self.pages = -1

    def get(self, idx: int) -> Item:
        item = self.items[idx]
        if isinstance(item, Item):
            return item # dont need to refetch the data
        self.items[idx] = Item.use(item)
        return self.items[idx]

    def add(self, product_box_soup):
        self.items.append(SimpleItem.parse(product_box_soup))

    def parse(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        if not self.init:
            countElm = soup.find('font', class_='count')
            if not countElm:
                self.maxItems = 0
                self.pages = 0
                self.init = True
                return
            self.maxItems = int(countElm.text)
            self.pages = int(ceil(self.maxItems / float(PER_PAGE)))
            self.init = True
        for product_box in soup.find_all('td', class_='product_box'):
            self.add(product_box)



SEARCH_URL = "http://slist.amiami.com/top/search/list?s_keywords={query}&pagemax={pagemax}&getcnt=0&pagecnt={page}"
PER_PAGE = 40
def search(keywords: str) -> ResultSet:
    data = {
        "query": keywords,
        "page": 1,
        "pagemax": PER_PAGE
    }
    rs = ResultSet()
    response = requests.get(SEARCH_URL.format(**data))
    print(response.url)
    rs.parse(response.text)
    while data['page'] < rs.pages:
        data['page'] += 1
        rs.parse(requests.get(SEARCH_URL.format(**data)).text)
    return rs
