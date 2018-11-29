import pandas as pd
from helpers import generate_random_payments, convert_to_df


def test_generate_random_payments_and_convert_to_df():
    df = convert_to_df(generate_random_payments())
    assert isinstance(df, (pd.DataFrame))
    assert df['income'].sum() == 1000000
