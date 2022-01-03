import pandas as pd
from preprocessing.prepare_config_files import prepare_token_params_sample


df_token_params = prepare_token_params_sample()


class Token:

    def get_token_params(self):
        df = df_token_params.copy(deep=True)
        df = df[df['Token_type'] == str(self.token_type)]
        df = df.to_dict()
        self.initial_price = df['Initial_price'][0]
        self.vesting_period = df['Vesting_period'][0]
        self.cliff_period = df['Cliff_period'][0]

    def __init__(self, **kwargs):

        # By default minter owns a token
        self.owner = 'minter'

        # All params are None
        self.initial_price = None
        self.cliff_period = None
        self.vesting_period = None
        self.token_type = kwargs.get('token_type', None)
        self.get_token_params()


class SeedToken(Token):
    def __init__(self):

        self.token_type = 'Seed'
        super(SeedToken, self).__init__(token_type=self.token_type)





