import requests
from bs4 import BeautifulSoup
import pandas as pd
from helpers.toml_tools import currency_mapping

currency_map = currency_mapping()


def get_poetrade_data(pay_currency: str, recv_currency: str):
    poetrade_url = f'https://currency.poe.trade/search?league=Kalandra&online=x&stock=&want={recv_currency}&have={pay_currency}'
    columns = ['pay_currency', 'pay_price', 'recv_currency', 'recv_price']
    req = requests.get(poetrade_url)
    soup = BeautifulSoup(req.content, 'html.parser', from_encoding='utf-8')
    result1 = soup.find(id="content").find_all('div', class_='displayoffer')
    _safe_value = 200.0

    df = pd.DataFrame(columns=columns)
    while df.shape[0] < 1:
        for element in result1:
            try:
                pay_currency = element['data-buycurrency']
                if float(element['data-buyvalue']) > _safe_value:
                    raise ValueError
                else:
                    pay_price = float(element['data-buyvalue'])
                recv_currency = element['data-sellcurrency']
                if float(element['data-sellvalue']) > _safe_value:
                    raise ValueError
                else:
                    recv_price = float(element['data-sellvalue'])
            except KeyError:
                # go to next result
                continue
            except ValueError:
                # go to next result
                continue
            else:
                if pay_price > 1:
                    pay_price = round(pay_price/recv_price, 2)
                    recv_price = 1
                df = pd.DataFrame([[currency_map[pay_currency], pay_price, currency_map[recv_currency], recv_price]], columns=columns)
                df_ret = df.to_dict('records')[0]
                break
    return df_ret
