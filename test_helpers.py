import pandas as pd
from helpers import generate_random_payments, convert_to_df, process_ingress_payments
from tokenomics import ERC20Token, Bucket


def test_generate_random_payments_and_convert_to_df():
    result = convert_to_df(generate_random_payments())
    assert isinstance(result, (pd.DataFrame))
    assert result['income'].sum() == 1000000


def test_generate_random_payments_and_process():
    rand_p = generate_random_payments()
    token = ERC20Token()
    bkt_two = Bucket(token=token, name="02")
    bkt_one = Bucket(token=token, max_volume=1000, overflow_bkt=bkt_two, name="01")
    res = process_ingress_payments(rand_p, token, bkt_one, bkt_two)
    assert isinstance(res,(tuple))
    res = convert_to_df(res)
    assert res['income'].sum() == 1000000
    assert res['01'].iloc[-1] == 1000
    assert res['02'].iloc[-1] == 1000000-1000



