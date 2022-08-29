import requests
from bs4 import BeautifulSoup
import pandas as pd
from helpers.toml_tools import currency_mapping

currency_map = currency_mapping()


def get_poetrade_data(pay_currency: str, recv_currency: str):
    poetrade_url = f'https://currency.poe.trade/search?league=Kalandra&online=x&stock=&want={pay_currency}&have={recv_currency}'
    columns = ['pay_currency', 'pay_value', 'recv_currency', 'recv_value']
    req = requests.get(poetrade_url)
    soup = BeautifulSoup(req.content, 'html.parser', from_encoding='utf-8')
    result1 = soup.find(id="content").find_all('div', class_='displayoffer')

    df = pd.DataFrame(columns=columns)
    while df.shape[0] < 1:
        for element in result1:
            try:
                pay_currency = element['data-buycurrency']
                pay_value = float(element['data-buyvalue'])
                recv_currency = element['data-sellcurrency']
                recv_value = float(element['data-sellvalue'])
            except KeyError:
                # go to next result
                continue
            finally:
                if recv_value > 1:
                    pay_value = round(pay_value/recv_value, 2)
                    recv_value = 1
                df = pd.DataFrame([[currency_map[pay_currency], pay_value, currency_map[recv_currency], recv_value]], columns=columns)
                df_ret = df.to_dict('records')[0]
                break
    return df_ret
