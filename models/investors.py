from random import random

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
        self.activity_coefficient = random.random()
        self.group = kwargs.get('group', 'Seed')

        if self.group not in token_types:
            raise ValueError(f'Group type of investor should be one of: {token_types}')

        num_months = kwargs.get('num_months', 48)

        # Create DataFrame with parameters of tokens
        cols_tokens = ['Token_type', 'Num', 'Initial_price', 'SbPool_flag', 'DivFarm_flag']
        self.df_tokens = pd.DataFrame(columns=cols_tokens)
        self.df_tokens['Token_type'] = token_types

        # Add number of month to tokens DataFrame
        days_data = {'Day_of_purchase': [i for i in range(1, (num_months + 1) * 30)]}
        df_months = pd.DataFrame(data=days_data)
        self.df_tokens = pd.merge(self.df_tokens, df_months, how='cross')

        # Fill null values
        self.df_tokens['DivFarm_flag'].fillna(False, inplace=True)
        self.df_tokens['SbPool_flag'].fillna(False, inplace=True)
        self.df_tokens['Num'].fillna(0, inplace=True)

    def add_tokens(self, params_tokens: dict, day: int):

        groups_tokens = params_tokens.keys()

        # Go though all groups of tokens
        for group in groups_tokens:

            # Get number of tokens for the group and add them to the investor
            num_tokens = params_tokens[group]
            if num_tokens != 0:
                self.df_tokens.loc[(self.df_tokens['Day_of_purchase'] == day) & (self.df_tokens['Token_type'] == group),
                                   ['Num']] += num_tokens

