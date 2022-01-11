import pandas as pd
from preprocessing.prepare_config_files import prepare_token_params_sample


df_token_params = prepare_token_params_sample()
df_token_types = df_token_params['Token_type']


class Farm:
    def __init__(self, **kwargs):

        self.type_farm = kwargs.get('type', 'SbPool')
        num_days = kwargs.get('days_num', 60 * 30)

        # Add 4 additional columns for days to get
        cols_days = [i for i in range(1, num_days + 5)]

        cols_tokens = ['Token_type'] + cols_days
        self.tokens = pd.DataFrame(columns=cols_tokens)
        self.tokens['Token_type'] = df_token_types

        # Fill null values
        self.tokens.fillna(0, inplace=True)

    def get_tokens_amount(self, day: int) -> int:
        """
        Gets total amount of tokens in Farm
        :param day: number of day
        :return: int, number of tokens
        """

        amount = self.tokens[day].sum()
        return amount

    def add_tokens(self, params_tokens: dict, day: int):
        """
        Adds tokens of different type
        :param params_tokens:
        :param day:
        :return:
        """
        for group in params_tokens.keys():
            num_tokens = int(params_tokens[group])
            if num_tokens != 0:
                self.tokens.loc[self.tokens['Token_type'] == group, [day]] += num_tokens

    def update(self, day: int):
        """
        Update Farm before the next day
        :param day: number of the current day
        """
        self.tokens[day + 1] = self.tokens[day]