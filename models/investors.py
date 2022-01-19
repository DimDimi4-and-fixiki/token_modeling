from random import random

import pandas as pd
import numpy as np
from preprocessing.prepare_config_files import prepare_token_params_sample
from models.farms import Farm
from utilities.py_tools import get_month_by_day

df_token_params = prepare_token_params_sample()
token_types = df_token_params['Token_type'].values
INF = 1e7


class Investor:
    def __init__(self, **kwargs):

        # Risk coefficient of the investor
        self.risk_coefficient = kwargs.get('risk_coefficient', None)
        self.activity_coefficient = random()
        self.group = kwargs.get('group', 'Seed')

        if self.group not in token_types:
            raise ValueError(f'Group type of investor should be one of: {token_types}')

        num_months = kwargs.get('num_months', 48)

        # Create DataFrame with parameters of tokens
        cols_tokens = ['Token_type', 'Num', 'Initial_price', 'SbPool_flag', 'DivFarm_flag', 'Day_of_freeze']
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
        self.df_tokens['Day_of_freeze'] = int(-INF)

    def add_tokens(self, params_tokens: dict, day: int):

        groups_tokens = params_tokens.keys()

        # Go though all groups of tokens
        for group in groups_tokens:

            # Get number of tokens for the group and add them to the investor
            num_tokens = params_tokens[group]
            if num_tokens != 0:
                self.df_tokens.loc[(self.df_tokens['Day_of_purchase'] == day) & (self.df_tokens['Token_type'] == group),
                                   ['Num']] += num_tokens

    def transfer_active_tokens(self, farm: Farm, day: int, freeze_period: int):

        # Name of column for needed Farm
        flag_farm = 'SbPool_flag' if farm.type_farm == 'SbPool' else 'DivFarm_flag'
        flag_opposite_farm = 'DivFarm_flag' if flag_farm == 'SbPool_flag' else 'SbPool_flag'

        # Get DataFrame of active tokens
        df_active_tokens = self.df_tokens[(self.df_tokens['Day_of_freeze'] <= day - freeze_period)
                                          & (self.df_tokens[flag_farm] == False) &
                                          (self.df_tokens['Day_of_purchase'] <= day)]

        # Mark tokens as transferred to the needed Farm
        df_active_tokens[flag_opposite_farm] = False
        df_active_tokens[flag_farm] = True
        df_active_tokens['Day_of_freeze'] = day

        # Change initial Data Frame with investors tokens
        self.df_tokens[(self.df_tokens['Day_of_freeze'] <= day - freeze_period)
                       & (self.df_tokens[flag_farm] == False) &
                       (self.df_tokens['Day_of_purchase'] <= day)] = df_active_tokens

        # Fill dictionary with active tokens parameters
        params_active_tokens = {}
        for group in token_types:
            params_active_tokens[group] = df_active_tokens[df_active_tokens['Token_type'] == group]['Num'].sum()

        # todo: Do minus tokens from current farm
        # Add all active tokens to the Farm
        farm.add_tokens(params_tokens=params_active_tokens, day=day)

