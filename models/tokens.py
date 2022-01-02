import pandas as pd


class Token:
    def __init__(self):

        # By default minter owns a token
        self.owner = 'minter'
        self.initial_price = None
        self.cliff_period = None
        self.vesting_period = None


class SeedToken(Token):
    def __init__(self):
        super(SeedToken, self).__init__()
        self.token_type = 'Seed'

        # note: add token price and cliff/vesting periods from config


