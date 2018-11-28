from helpers import generate_random_payments, convert_to_df
import pandas as pd

def test_generate_random_payments_and_convert_to_df():
    df = convert_to_df(generate_random_payments())
    assert type(df) == pd.DataFrame
    assert df['income'].sum() == 1000000


