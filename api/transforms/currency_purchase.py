from getters.poe_trade import get_poetrade_data
from getters.rmt_site import get_rmt_data
from helpers.weight_sentences import weighting_sentences
import pendulum

def currency_purchase(pay_currency: int, recv_currency: int, method: str = 'simple'):
    rmt = get_rmt_data(str(pay_currency), str(recv_currency))
    poe = get_poetrade_data(str(pay_currency), str(recv_currency))

    rmt_recv_price = float(rmt['recv_price'])
    poe_recv_price = float(poe['recv_price'])
    rmt_pay_price = float(rmt['pay_price'])
    poe_pay_price = float(poe['pay_price'])
    
    recv_cost = rmt_recv_price * poe_recv_price
    pay_cost = rmt_pay_price * poe_pay_price
    rmt_diff = round(recv_cost - pay_cost, 2)
    rmt_diff_percent = round(rmt_diff / rmt_pay_price * 100, 2)
    if rmt_diff_percent < 0:
        rmt_buy_currency = rmt['recv_currency']
    else:
        rmt_buy_currency = rmt['pay_currency']
    
    # weights depending on rmt_diff_percent
    rmt_weight = weighting_sentences(rmt_diff_percent)
    
    timestamp = pendulum.now().to_datetime_string()
    
    if method == 'detailed':
        d = {'pay_currency': poe['pay_currency'], 'pay_price_poe': poe['pay_price'],
             'recv_currency': poe['recv_currency'], 'recv_price_poe': poe['recv_price'],
             'pay_price_rmt': rmt['pay_price'], 'recv_price_rmt': rmt['recv_price'],
             'rmt_recommendation': rmt_buy_currency, 'rmt_recommendation_weight': rmt_weight,
             'pay_price_rmt_diff': rmt_diff, 'pay_price_rmt_diff_percent': rmt_diff_percent,
             'timestamp': timestamp}
    elif method == 'simple':
        d = {'pay_currency': poe['pay_currency'], 'recv_currency': poe['recv_currency'],
             'rmt_recommendation': rmt_buy_currency, 'rmt_recommendation_weight': rmt_weight,
             'timestamp': timestamp}
    return d