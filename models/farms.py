import pandas as pd
from preprocessing.prepare_config_files import prepare_token_params_sample


df_token_params = prepare_token_params_sample()
df_token_types = df_token_params['Token_type']


class Farm:
    def __init__(self, **kwargs):

        self.type_farm = kwargs.get('type', 'SbPool')
        num_days = kwargs.get('days_num', 60 * 30)

        types_tokens = df_token_types.copy(deep=True)

        # In SbPool we also keep number of BNB tokens
        if self.type_farm == 'SbPool':
            bnb_row = pd.Series(['BNB'])
            types_tokens = types_tokens.append(bnb_row).reindex()

        # Generate list with number of days for modelling
        cols_days = [i for i in range(1, num_days + 5)]

        # Columns for tokens DataFrame
        cols_tokens = ['Token_type'] + cols_days

        # Create tokens DataFrame and fill Nulls
        self.tokens = pd.DataFrame(columns=cols_tokens)
        self.tokens['Token_type'] = types_tokens
        self.tokens.fillna(0, inplace=True)

    def get_tokens_amount(self, day: int) -> float:
        """
        Gets total amount of tokens in Farm
        :param day: number of day
        :return: int, number of tokens
        """

        # Get sum of all Smarty tokens
        amount = self.tokens[self.tokens['Token_type' != 'BNB']][day].sum()
        return amount

    def get_bnb_amount(self, day: int) -> float:

        # Get sum of all Smarty tokens
        amount = self.tokens[self.tokens['Token_type' == 'BNB']][day].sum()
        return amount

    def get_currency_rate(self, day: int) -> float:
        """
        Returns BNB / Smarty ratio in SbPool
        :param day: number of the current day
        :return:
        """

        smarty_amount = self.get_tokens_amount()
        bnb_amount = self.get_bnb_amount()

        return bnb_amount / smarty_amount

    def add_tokens(self, params_tokens: dict, day: int, currency_rate=None):
        """
        Adds tokens to the Farm
        :param currency_rate: currency rate, could be specified by adding Smarty tokens manually
        :param params_tokens: dictionary with (token_type: num_tokens)
        :param day: number of the current day
        """

        # Loop through each group of tokens
        for group in params_tokens.keys():
            num_tokens = int(params_tokens[group])
            if num_tokens != 0:

                # Update tokens DataFrame by adding Smarty tokens
                self.tokens.loc[self.tokens['Token_type'] == group, [day]] += num_tokens

                # If we are adding Smarty to SbPool, we also need to add BNB
                if self.type_farm == 'SbPool':
                    if currency_rate is None:
                        currency_rate = self.get_currency_rate(day=day)

                    # Add BNB tokens to the tokens DataFrame
                    num_bnb = num_tokens * currency_rate
                    self.tokens.loc[self.tokens['Token_type'] == 'BNB', [day]] += num_bnb

    def update(self, day: int):
        """
        Update Farm before the next day by transferring all data to the next day
        :param day: number of the current day
        """

        # Copy all data for the current day as initial data of the next day
        self.tokens[day + 1] = self.tokens[day]