import requests
from bs4 import BeautifulSoup, element
from math import ceil
import re
from urllib.parse import urlencode

rootURL = "https://www.amiami.com"
class SimpleItem:
    def __init__(self, *args, **kwargs):
        self.productURL = kwargs['productURL']
        self.imageURL = kwargs['imageURL']
        self.productName = kwargs['productName']
        self.price = kwargs['price']
        self.productCode = kwargs['productCode']

    @staticmethod
    def parse(product_box_soup: element.Tag):
        data = {
            'productURL': "{}{}".format(rootURL, product_box_soup.find('a')['href']),
            'productCode': product_box_soup.find('a')['href'],
            'imageURL': product_box_soup.find('img')['src'],
            'productName': product_box_soup.find("p",class_="newly-added-items__item__name").text,
            # for some reason, it has a bunch of tabs everywhere for spacing
            'price': product_box_soup.find("p", class_="newly-added-items__item__price").text.strip(),
        }
        data['productCode'] = re.search('gcode=(.*)', data['productCode']).group(1)
        # process some stuff
        data['price'] = re.search("(.*)[^,\d]", data['price']).group(1)
        return SimpleItem(**data)

def removeSuffix(str, suffix):
    if str.endswith(suffix):
        return str[: -1*len(suffix)]

class Item(SimpleItem):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.availability = kwargs['availability']
        self.about = kwargs['about']

    @staticmethod
    def use(simpleItem: SimpleItem):
        MAX_ATTEMPTS = 10
        currAttempt = 0
        while currAttempt < MAX_ATTEMPTS:
            try:
                url = simpleItem.productURL
                data = vars(simpleItem)
                data['about'] = {}
                r = requests.get(RENDER_URL,
                    params={
                        'url':url,
                        'wait':3})
                soup = BeautifulSoup(r.text, 'html.parser')

                data['productName'] = soup.find('h2', class_='item-detail__section-title').text

                def shown_btn_cart(tag):
                    return "btn-cart" in tag['class'] and tag['style'] != "display: none;"

                a = soup.find("div", class_="item-detail__operation__inner").find(shown_btn_cart)
                data['availability'] = a.text

                abouts = soup.find("section", class_="item-about").find_all("dt", class_="item-about__data-title")
                for titleTag in abouts:
                    sib = titleTag.next_sibling
                    # skip if it doesn't have a corresponding text, should never happen
                    if 'item-about__data-text' not in sib['class']:
                        continue
                    key = titleTag.text.replace(' ', '')
                    val = sib.text
                    data['about'][key] = val

                return Item(**data)
            except AttributeError as e:
                #print(soup)
                currAttempt += 1
                print("Retrying page load, failed {} time(s)".format(currAttempt))
                continue
        else:
            raise AttributeError("Could not successfully generate info")


class ResultSet:

    def __init__(self):
        self.items = []
        self.maxItems = -1
        self.init = False
        self.pages = -1
        self._itemCount = 0

    def get(self, idx: int) -> Item:
        item = self.items[idx]
        if isinstance(item, Item):
            return item # dont need to refetch the data
        self.items[idx] = Item.use(item)
        return self.items[idx]

    def add(self, product_box_soup):
        self.items.append(SimpleItem.parse(product_box_soup))

    def parse(self, html):
    # returns true when done
    # false if can be called again
        soup = BeautifulSoup(html, 'html.parser')
        if not self.init:
            countElm = soup.find('p', class_='search-result__text')
            if not countElm:
                self.maxItems = 0
                self.pages = 0
                self.init = True
                return True
            # countElm.text := "81-100 of 3377 results" or something
            self.maxItems = int(re.search('of (\d+)', countElm.text).group(1))
            self.pages = int(ceil(self.maxItems / float(PER_PAGE)))
            self.init = True
        for product_box in soup.find_all('li', class_='newly-added-items__item'):
            self.add(product_box)
            self._itemCount += 1

        return self._itemCount == self.maxItems

# 172... is the local ip of docker service containing splash service
# wait about 5s to be sure that everything loaded
# need to make this dynamic eventually and allow ip to be passed
RENDER_URL = "http://172.17.0.1:8080/render.html"
PER_PAGE = 20 # this is hardcoded and not really used tho
def search(keywords: str) -> ResultSet:
    print("hell1o")
    data = {
        "s_keywords": keywords,
        "pagecnt": 1,
    }
    rs = ResultSet()
    while not rs.parse(requests.get(RENDER_URL,
        params={
            'url':'https://www.amiami.com/eng/search/list?{}'.format(urlencode(data)),
            'wait':5}).text):

        data['pagecnt'] += 1
    return rs
