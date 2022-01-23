import pandas as pd
from preprocessing.prepare_config_files import prepare_token_params_sample
from utilities.py_tools import log

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
            self.initial_tokens = kwargs.get('params_tokens', {'Seed': 0})

        # Generate list with number of days for modelling
        cols_days = [i for i in range(1, num_days + 5)]

        # Columns for tokens DataFrame
        cols_tokens = ['Token_type'] + cols_days

        # Create tokens DataFrame and fill Nulls
        self.tokens = pd.DataFrame(columns=cols_tokens)
        self.tokens['Token_type'] = types_tokens
        self.tokens.fillna(0, inplace=True)

        # Dividends DataFrame contains only days columns
        cols_dividends = ['Dividends_type'] + cols_days
        self.dividends = pd.DataFrame(columns=cols_dividends)

        # Dividends could come from turnover or from minting new tokens
        self.dividends['Dividends_type'] = pd.Series(['Turnover', 'Minted'])
        self.dividends.fillna(0, inplace=True)

    def get_tokens_amount(self, day: int, all=False) -> float:
        """
        Gets total amount of Smarty tokens in Farm
        :param all: flag if we need to include initial tokens that we put in Farm
        :param day: number of day
        :return: int, number of tokens
        """

        # Get sum of all Smarty tokens in farm
        amount = self.tokens[self.tokens['Token_type'] != 'BNB'][day].sum()

        # In SbPool we do not count tokens that we put here at the start
        if self.type_farm == 'SbPool' and not all:
            amount -= sum(list(self.initial_tokens.values()))

        return amount

    def get_bnb_amount(self, day: int) -> float:

        # Get sum of all Smarty tokens
        amount = self.tokens[self.tokens['Token_type'] == 'BNB'][day].sum()
        return amount

    def get_currency_rate(self, day: int) -> float:
        """
        Returns BNB / Smarty ratio in SbPool
        :param day: number of the current day
        :return:
        """

        smarty_amount = self.get_tokens_amount(day=day, all=True)
        bnb_amount = self.get_bnb_amount(day=day)

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

                # If we are adding Smarty to SbPool, we also need to add BNB
                if self.type_farm == 'SbPool':
                    if currency_rate is None:
                        currency_rate = self.get_currency_rate(day=day)

                    # Add BNB tokens to the tokens DataFrame according to Smarty rate
                    num_bnb = num_tokens * currency_rate
                    self.tokens.loc[self.tokens['Token_type'] == 'BNB', [day]] += num_bnb

                # Update tokens DataFrame by adding Smarty tokens
                self.tokens.loc[self.tokens['Token_type'] == group, [day]] += num_tokens

    def remove_tokens(self, params_tokens: dict, day: int, currency_rate=None):
        """
        Removes tokens from the Farm
        :param currency_rate: currency rate, could be specified by adding Smarty tokens manually
        :param params_tokens: dictionary with (token_type: num_tokens)
        :param day: number of the current day
        """

        # To remove tokens we need to get the same dict but with negative values
        dict_tokens = {}
        for group in params_tokens.keys():
            dict_tokens[group] = -params_tokens[group]

        # Remove tokens by adding negative amounts of tokens to the Farm
        self.add_tokens(params_tokens=dict_tokens, day=day, currency_rate=currency_rate)

    def __add_smarty_dividends(self, num_tokens: float, day: int, type_dividends: str):
        """
        Private method for adding Smarty tokens to dividends
        :param num_tokens: number of tokens
        :param day: number of the current day
        :param type_dividends: dividends type, one of ('Turnover', 'Minted')
        :return:
        """

        # Updates dividends DataFrame
        self.dividends.loc[self.dividends['Dividends_type'] == type_dividends, [day]] += num_tokens

    def add_dividends(self, day: int, bnb_smarty_rate=None, num_tokens=None, type_operation='bnb',
                      type_dividends='Turnover', index_revenue=None):
        """
        :param bnb_smarty_rate: current BNB / Smarty rate
        :param num_tokens: number of tokens (Smarty or BNB) to add
        :param day: number of the current day
        :param type_operation: type of the operation:
            1) 'bnb' - add a specified number of BNB tokens (by current BNB / Smarty rate)
            2) 'smarty' - add a specified number of Smarty tokens
            3) 'index_revenue' - add Smarty tokens to set (dividends / num_tokens) >= min_profit
        :param index_revenue: minimum profit that we want to set
        """

        # If we want to add Smarty tokens
        if type_operation == 'smarty':
            self.__add_smarty_dividends(day=day, num_tokens=num_tokens, type_dividends=type_dividends)

        # Add a specified number of BNB tokens
        elif type_operation == 'bnb':

            # To add BNB tokens we convert them to Smarty by current currency rate
            if bnb_smarty_rate is None:
                bnb_smarty_rate = self.get_currency_rate(day=day)

            num_smarty = num_tokens / bnb_smarty_rate
            self.__add_smarty_dividends(day=day, num_tokens=num_smarty, type_dividends=type_dividends)

        elif type_operation == 'index_revenue':

            current_index_revenue = self.get_current_dividends(day=day) / self.get_tokens_amount(day=day)

            # If current revenue index is big enough, we don't add tokens
            if current_index_revenue >= index_revenue:
                log(f'On day={day} revenue index in {self.type_farm} = {current_index_revenue} > {index_revenue}')
                return
            else:
                # Calculate number of tokens and add them to dividends
                delta_index = index_revenue - current_index_revenue
                num_smarty = delta_index * self.get_tokens_amount(day=day)
                self.__add_smarty_dividends(day=day, num_tokens=num_smarty, type_dividends=type_dividends)

    def get_current_dividends(self, day: int) -> float:
        return self.dividends[day].sum()

    def clear_dividends(self, day: int):
        self.dividends[day] = 0.0

    def update(self, day: int, clear_dividends=False):
        """
        Update Farm before the next day by transferring all data to the next day
        :param clear_dividends: flag if dividends were payed on the current day
        :param day: number of the current day
        """

        # Copy all data for the current day as initial data of the next day
        self.tokens[day + 1] = self.tokens[day]

        if not clear_dividends:
            self.dividends[day + 1] = self.dividends[day]
        else:
            self.dividends[day + 1] = 0.0
