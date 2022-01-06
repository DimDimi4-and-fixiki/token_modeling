import pandas as pd
import numpy as np

from utilities.py_tools import get_distribution_by_sum, get_month_by_day
from models.investors import Investor


def create_investors(params_investors: dict, params_modelling: dict) -> dict:

    # Dictionary for the results
    investors = {}

    # Risk coefficient
    mu, sigma = params_modelling['mu'], params_modelling['sigma']
    num_months = params_modelling['num_months']

    # Create investors for all groups
    for group in params_investors.keys():
        investors[group] = []
        num_investors = params_investors[group]
        for i in range(num_investors):
            risk_coeff = np.random.normal(mu, sigma, 1)[0]
            investor = Investor(group=group, risk_coefficient=risk_coeff, num_months=num_months)
            investors[group].append(investor)

    return investors


def sell_tokens(investors: dict, params_tokens: dict, day: int):

    # Loop through all groups of investors
    for group in params_tokens.keys():
        investors_group = investors[group]
        num_tokens = params_tokens[group]
        num_investors = len(investors_group)

        # Get distribution of tokens between investors
        distr_tokens = get_distribution_by_sum(sum=num_tokens, size=num_investors)

        # Give tokens to investors
        for index, investor in enumerate(investors_group):
            n_tokens = distr_tokens[index]
            investor.add_tokens(day=day, num_tokens=n_tokens)


def get_mint_distribution_by_day(mint_distr: pd.DataFrame, day: int) -> dict:

    # Create zeroes dictionary with all tokens types
    res_distr = {}
    types = mint_distr['Token_type'].unique()
    for t in types:
        res_distr[t] = 0

    # If day is the first day in month
    if (day - 1) % 30 == 0:
        num_month = get_month_by_day(day=day)

        # todo: handle case: num_month > DataFrame index
        df = mint_distr[['Token_type', num_month]].copy(deep=True).to_dict()

        # Get token types and token amounts from DataFrame
        token_types = df['Token_type']
        token_nums = df[num_month]

        # Fill dictionary with values
        for index in token_types.keys():
            token_type, token_num = token_types[index], token_nums[index]
            res_distr[token_type] = token_num

        return res_distr




