import pandas as pd
from preprocessing.prepare_config_files import prepare_token_params_sample


# Read token parameters for all types of tokens
df_token_params = prepare_token_params_sample()


# Base class for Token
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
        self.purchase_day = kwargs.get('purchase_day', None)
        self.current_price = self.initial_price
        self.get_token_params()


class SeedToken(Token):
    def __init__(self):
        self.token_type = 'Seed'
        super(SeedToken, self).__init__(token_type=self.token_type)


class PrivateSaleToken(Token):
    def __init__(self):
        self.token_type = 'Private sale'
        super(SeedToken, self).__init__(token_type=self.token_type)


class PublicSaleToken(Token):
    def __init__(self):
        self.token_type = 'Public sale'
        super(SeedToken, self).__init__(token_type=self.token_type)


class TeamToken(Token):
    def __init__(self):
        self.token_type = 'Team'
        super(SeedToken, self).__init__(token_type=self.token_type)


class CommunityToken(Token):
    def __init__(self):
        self.token_type = 'Community'
        super(SeedToken, self).__init__(token_type=self.token_type)


class StakingRewardsToken(Token):
    def __init__(self):
        self.token_type = 'Staking rewards'
        super(SeedToken, self).__init__(token_type=self.token_type)






