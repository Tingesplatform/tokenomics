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
        payments.append([datetime.fromtimestamp(random_date), amount])
        sum_of_payments += amount
    payments = sorted(payments, key=lambda x: x[0])
    column_names = ['date', 'income']
    return column_names, payments


def process_ingress_payments(payments_set, token, entry_bucket, *args):
    column_names = payments_set[0]
    values = payments_set[1]
    for payment in values:
        token.mint(entry_bucket, payment[1])
        entry_bucket.flush()
        for i in [entry_bucket] + list(args):
            payment.append(token.balance_of(i))
    for i in [entry_bucket] + list(args):
        column_names.append(i.name)
    return column_names, values


def convert_to_df(payments_set):
    df = pd.DataFrame(payments_set[1], columns=payments_set[0])
    df = df.set_index('date')
    return df
