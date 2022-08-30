import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import List, Dict
from helpers.toml_tools import load_toml, currency_mapping


CONFIG = load_toml()
TRUSTED_SELLERS: Dict[str,str] = CONFIG['trusted_sellers']
currency_map = currency_mapping()

def get_rmt_data(pay_currency_id: str, recv_currency_id: str):
    columns = ['pay_currency', 'pay_price', 'recv_currency', 'recv_price']
    df = pd.DataFrame(columns=columns)
    URLS = [x['url'] for x in CONFIG.get('currencies') if x['id'] == pay_currency_id or x['id'] == recv_currency_id]
    for url in URLS:
        req = requests.get(url)
        soup = BeautifulSoup(req.content, 'html.parser', from_encoding='utf-8')
        result1 = soup.find(id="pre_checkout_sls_offer")
        result2 = result1.find_all('div', class_='other_offer-desk-main-box')

        for element in result2:
            seller = element.find('div', class_='seller__name-detail')
            if seller.text in TRUSTED_SELLERS:
                price = element.find('span', class_='offer-price-amount')
                if currency_map[pay_currency_id] in url:
                    df.at[0, 'pay_currency'] = currency_map[pay_currency_id]
                    df.at[0, 'pay_price'] = price.text
                if currency_map[recv_currency_id] in url:
                    df.at[0, 'recv_currency'] = currency_map[recv_currency_id]
                    df.at[0, 'recv_price'] = price.text
            else:
                pass
    return df.to_dict('records')[0]
