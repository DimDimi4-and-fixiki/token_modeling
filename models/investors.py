import pandas as pd
import numpy as np
from preprocessing.prepare_config_files import prepare_token_params_sample
from utilities.py_tools import get_month_by_day


df_token_params = prepare_token_params_sample()
token_types = df_token_params['Token_type'].values


class Investor:
    def __init__(self, **kwargs):

        # Risk coefficient of the investor
        self.risk_coefficient = kwargs.get('risk_coefficient', None)
        self.group = kwargs.get('group', 'Seed')

        if self.group not in token_types:
            raise ValueError(f'Group type of investor should be one of: {token_types}')

        num_months = kwargs.get('num_months', 48)

        # Parameters of tokens
        cols_tokens = ['Token_type', 'Num', 'Initial_price', 'SbPool_flag', 'DivFarm_flag']
        self.df_tokens = pd.DataFrame(columns=cols_tokens)
        self.df_tokens['Token_type'] = [self.group]

        # Add number of month to tokens DataFrame
        months_data = {'Month_of_purchase': [i for i in range(0, num_months + 1)]}
        df_months = pd.DataFrame(data=months_data)
        self.df_tokens = pd.merge(self.df_tokens, df_months, how='cross')

        # Fill null values
        self.df_tokens['DivFarm_flag'].fillna(False, inplace=True)
        self.df_tokens['SbPool_flag'].fillna(False, inplace=True)
        self.df_tokens['Num'].fillna(0, inplace=True)

    def add_tokens(self, num_tokens: int, day: int):
        month = get_month_by_day(day)
        self.df_tokens.loc[self.df_tokens['Month_of_purchase'] == month, ['Num']] += num_tokens

