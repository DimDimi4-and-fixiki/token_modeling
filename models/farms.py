import pandas as pd
from preprocessing.prepare_config_files import prepare_token_params_sample


df_token_params = prepare_token_params_sample()
df_token_types = df_token_params['Token_type']


class Farm:
    def __init__(self, **kwargs):
        num_days = kwargs.get('days_num', 60 * 30)
        cols_days = [f'day_{i}' for i in range(1, num_days + 1)]

        cols_tokens = ['Token_type'] + cols_days
        self.tokens = pd.DataFrame(columns=cols_tokens)
        self.tokens['Token_type'] = df_token_types