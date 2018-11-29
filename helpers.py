from datetime import datetime
from random import randint
import pandas as pd


def generate_random_payments(date_range=(datetime(2019, 1, 1), datetime(2020, 1, 1)),
                             amount_range=(100, 10000),
                             value=1000000):
    payments = []
    sum_of_payments = 0
    while sum_of_payments < value:
        random_date = randint(date_range[0].timestamp(), date_range[1].timestamp())
        amount = randint(amount_range[0], amount_range[1])
        if amount + sum_of_payments > value:
            amount = value - sum_of_payments
        payments.append((datetime.fromtimestamp(random_date), amount))
        sum_of_payments += amount
    payments = sorted(payments, key=lambda x: x[0])
    return payments


def convert_to_df(data, columns=('date', 'income')):
    df = pd.DataFrame(data, columns=columns)
    df = df.set_index('date')
    return df
