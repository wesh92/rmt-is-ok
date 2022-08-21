from dataclasses import dataclass, field
import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import Dict, List
import tomli


def util_load_toml():
    rel_path = r'rmt-is-ok\src\python\configs\trusted_sellers.toml'
    with open(rel_path, mode='rb') as f:
        return tomli.load(f)

@dataclass
class TradeData:

    currency_map: Dict[str, str] = field(default_factory={
        "6": "EXALT",
        "4": "CHAOS",
        "15": "DIVINE"
        }
    )
    
    def _make_poetrade_urls_list(self, map_of_currency_to_id: Dict[str, str]
                                 = currency_map):
        poetrade_url = 'https://currency.poe.trade/search?league=Kalandra&online=x&stock=&want={}&have={}'
        return [poetrade_url.format(x, y) for x in map_of_currency_to_id for y in map_of_currency_to_id if x != y]

    def get_poetrade_data(self):

        # for every permutation of currency, get the price and add it to the dataframe
        columns = ['pay_currency', 'pay_value', 'recv_currency', 'recv_value', 'stock']
        df = pd.DataFrame(columns=columns)
        # take keys from currency_map and permute them
        url_list = self._make_poetrade_urls_list(self.currency_map)
        for url in url_list:
            sess = requests.session()
            req = sess.get(url)
            soup = BeautifulSoup(req.content, 'html.parser', from_encoding='utf-8')
            result1 = soup.find(id="content")
            result2 = result1.find_all('div', class_='displayoffer')

            for element in result2:
                try:
                    buy_currency = element['data-buycurrency']
                    buy_value = element['data-buyvalue']
                    sell_currency = element['data-sellcurrency']
                    sell_value = element['data-sellvalue']
                    data_stock = element['data-stock']
                except KeyError:
                    continue
                df2 = pd.DataFrame([[self.currency_map[buy_currency], buy_value, self.currency_map[sell_currency], sell_value, data_stock]], columns=columns)
                df = df.append(df2, ignore_index=True)
        return df


class RMTData:
    def __init__(self):
        self.CONFIG = util_load_toml()

    @property
    def URLS(self):
        return self.CONFIG['urls']

    @property
    def TRUSTED_SELLERS(self):
        return self.CONFIG['trusted_sellers']

    def get_rmt_data(self):
        columns = ['seller', 'currency', 'price']
        df = pd.DataFrame(columns=columns)
        for currency, url in self.URLS.items():
            sess = requests.session()
            req = sess.get(url)
            soup = BeautifulSoup(req.content, 'html.parser', from_encoding='utf-8')
            result1 = soup.find(id="pre_checkout_sls_offer")
            result2 = result1.find_all('div', class_='other_offer-desk-main-box')

            for element in result2:
                seller = element.find('div', class_='seller__name-detail')
                if seller.text in self.TRUSTED_SELLERS:
                    price = element.find('span', class_='offer-price-amount')
                    currency = currency
                    df2 = pd.DataFrame([[seller.text, currency, price.text]], columns=columns)
                    df = df.append(df2, ignore_index=True)
                else:
                    pass
        return df
        
        
a = RMTData().get_rmt_data()
print(a)