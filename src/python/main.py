from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import Dict, List, Union
import tomli
import pendulum
import os
from sqlalchemy import create_engine

pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)  

def util_load_toml():
    rel_path = r'rmt-is-ok\src\python\configs\trusted_sellers.toml'
    full_path = os.path.abspath(rel_path)
    with open(full_path, mode='rb') as f:
        return tomli.load(f)

@dataclass
class TradeData:

    currency_map = {
        "6": "EXALT",
        "4": "CHAOS",
        "15": "DIVINE",
        "24": "MIRROR"
        }
    
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

@dataclass
class RMTData:
    CONFIG = util_load_toml()

    @property
    def URLS(self):
        return self.CONFIG['urls']

    @property
    def TRUSTED_SELLERS(self):
        return self.CONFIG['trusted_sellers']

    def get_rmt_data(self, columns: List[str]):
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
        

class Transformations:
    def __init__(self):
        self.sell_columns = ['seller', 'recv_currency', 'recv_price']
        self.pay_columns = ['seller', 'pay_currency', 'pay_price']
        self.safe_limit: float = 300.0
        self.keep_recv_currency: Union[List[str, str], str] = 'CHAOS'
    
    @property
    def RECV_DATA(self):
        return RMTData().get_rmt_data(self.sell_columns)
    
    @property
    def PAY_DATA(self):
        return RMTData().get_rmt_data(self.pay_columns)
    
    @property
    def TRADE_DATA(self):
        return TradeData().get_poetrade_data()
    
    # function to merge the two dataframes joined on the currency type
    def merge_dataframes(self):
        df = pd.merge(self.PAY_DATA[['pay_price', 'pay_currency']], self.TRADE_DATA, on='pay_currency')
        df = pd.merge(df, self.RECV_DATA[['recv_price', 'recv_currency']], on='recv_currency')
        return df
    
    # only select the first instance of each pay and recv currency pair
    def select_first_instance(self):
        df = self.merge_dataframes()
        # remove anamlous rows > 200 recv currency
        df = df[df['recv_price'].astype(float) <= self.safe_limit]
        # only select rows where recv_currency is CHAOS
        if isinstance(self.keep_recv_currency, str):
            df = df[df['recv_currency'] == self.keep_recv_currency]
        elif isinstance(self.keep_recv_currency, list):
            df = df[df['recv_currency'].isin(self.keep_recv_currency)]
        else:
            raise ValueError('keep_recv_currency must be a list or string')
        # only select rows where pay_value is 1
        df = df[df['pay_value'].astype(float) <= 1] # the methodology here is a little skewed I know, but usually early rows are 1 chaos
        df = df.drop_duplicates(subset=['pay_currency', 'recv_currency'], keep='first')
        return df
    
    # math time, multiply the recv price by recv value.
    # then multiply the pay price by pay value.
    def create_prices_data(self):
        ts = pendulum.now().strftime('%Y-%m-%d %H:%M:%S')
        df = self.select_first_instance()
        recv_price = df['recv_price'].astype(float)
        recv_value = df['recv_value'].astype(float)
        pay_price = df['pay_price'].astype(float)
        pay_value = df['pay_value'].astype(float)
        df['recv_cost'] = recv_price * recv_value
        df['pay_cost'] = pay_price * pay_value
        df['rmt_diff'] = round(df['recv_cost'], 2) - round(df['pay_cost'], 2)
        df['rmt_diff_percent'] = df['rmt_diff'] / df['pay_cost']
        df['timestamp'] = ts
        return df
   

    def save_csv(self, input_df: pd.DataFrame):
        ts_short = pendulum.now().strftime('%Y-%m-%d-%H%M%S')
        # open a file in /src/data/ and write the dataframe to it
        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', f'rmt_data_{ts_short}.csv')), 'w+', newline='') as f:
            input_df.to_csv(f, index=False)

    def send_to_pg(self, input_df: pd.DataFrame):
        pg = create_engine('postgresql://user:password@localhost:5432/rmt_data', connect_args={'options': '-csearch_path=schema'})
        input_df.to_sql('rmt_data', pg, if_exists='append', index=False)
        

if __name__ == '__main__':
    t = Transformations()
    df = t.create_prices_data()
    t.save_csv(df)
    t.send_to_pg(df)
    
