import pandas as pd
from preprocessing.prepare_config_files import prepare_token_params_sample


df_token_params = prepare_token_params_sample()
df_token_types = df_token_params['Token_type']


class Investor:
    def __init__(self, **kwargs):

        # Risk coefficient of the investor
        self.risk_coefficient = kwargs.get('risk_coefficient', None)
        months_num = kwargs.get('months_num', 48)

        # Parameters of tokens
        cols_tokens = ['Token_type', 'Num', 'Initial_price', 'SbPool_flag', 'DivFarm_flag']
        self.df_tokens = pd.DataFrame(columns=cols_tokens)
        self.df_tokens['Token_type'] = df_token_types

        # Add number of month to tokens DataFrame
        months_data = {'Month_of_purchase': [i for i in range(0, months_num + 1)]}
        df_months = pd.DataFrame(data=months_data)
        self.df_tokens = pd.merge(self.df_tokens, df_months, how='cross')

        # Fill null values
        self.df_tokens['DivFarm_flag'].fillna(False, inplace=True)
        self.df_tokens['SbPool_flag'].fillna(False, inplace=True)
        self.df_tokens['Num'].fillna(0, inplace=True)

