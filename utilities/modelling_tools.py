import pandas as pd
import numpy as np

from utilities.py_tools import get_distribution_by_sum, get_month_by_day, log
from models.investors import Investor
from models.farms import Farm
import itertools


def create_investors(params_investors: dict, params_modelling: dict) -> dict:
    """
    Creates dictionary with lists of Investors objects for each type of investor
    :param params_investors: Params of investors
    :param params_modelling: Modelling params for investors
    :return: dictionary with Investor objects
    """

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


def sell_tokens(investors: dict, params_tokens: dict, day: int, excluded_tokens: list):

    # Loop through all groups of investors
    for group in params_tokens.keys():

        # Sell tokens for all groups of investors
        if group not in excluded_tokens:
            investors_group = investors[group]
            num_tokens = params_tokens[group]
            num_investors = len(investors_group)

            # Get distribution of tokens between investors
            distr_tokens = get_distribution_by_sum(sum=num_tokens, size=num_investors)

            # Give tokens to investors
            for index, investor in enumerate(investors_group):
                n_tokens = distr_tokens[index]
                dict_tokens = {group: n_tokens}
                investor.add_tokens(day=day, params_tokens=dict_tokens)


def get_mint_distribution_by_month(mint_distr: pd.DataFrame, num_month: int) -> dict:

    # Create zeroes dictionary with all tokens types
    types = mint_distr['Token_type'].unique()
    res_distr = {}
    for t in types:
        res_distr[t] = 0

    # Get all numbers of months from mint distribution
    cols_months = mint_distr.columns[1:].astype(int)

    # If current month > maximum month in mint distribution
    if cols_months.max() < num_month:
        return res_distr

    for t in types:
        df = mint_distr[['Token_type', num_month]].copy(deep=True).to_dict()

        # Get token types and token amounts from DataFrame
        token_types = df['Token_type']
        token_nums = df[num_month]

        # Fill dictionary with values
        for index in token_types.keys():
            token_type, token_num = token_types[index], token_nums[index]
            res_distr[token_type] = token_num

        return res_distr


def distribute_tokens_by_days(mint_distr: dict, num_days=30) -> dict:
    # Get all groups of tokens
    groups_tokens = mint_distr.keys()

    # Empty dictionary for the result
    res = {}

    for group in groups_tokens:
        num_tokens = mint_distr[group]
        res[group] = get_distribution_by_sum(sum=num_tokens, size=num_days)

    return res


def get_tokens_distribution_by_day(distribution_tokens_days: dict, day: int) -> dict:
    res = {}
    groups_tokens = distribution_tokens_days.keys()

    for group in groups_tokens:
        index = day - 1
        res[group] = distribution_tokens_days[group][index]

    return res


def investors_sorter(investor: Investor):
    return investor.activity_coefficient


def transfer_investors(sb_pool: Farm, div_farm: Farm, dict_investors: dict,
                       day: int, div_sb_pool: float, div_div_farm: float,
                       freeze_period: int):

    """
    Transfers tokens of investors in a more profitable farm
    :param freeze_period: number of days when token is frozen
    :param sb_pool: SbPool object
    :param div_farm: DivFarm object
    :param dict_investors: dict with all types of investors
    :param day: number of the current day
    :param div_sb_pool: number of dividends for SbPool
    :param div_div_farm: number of dividends for DivFarm
    """

    # todo: Now only Seed investors included (to save performance)
    dict_investors = {'Seed': dict_investors['Seed']}
    investors = list(itertools.chain.from_iterable(dict_investors.values()))

    # Sort investors in descending order by their coefficients of activity
    investors_sorted = sorted(investors, key=investors_sorter, reverse=True)

    for index, investor in enumerate(investors_sorted):
        num_tokens_sb_pool = sb_pool.get_tokens_amount(day=day)
        num_tokens_div_farm = div_farm.get_tokens_amount(day=day)

        # If we have no tokens in Div Farm (day = 1 case)
        if num_tokens_div_farm == 0:
            investor.transfer_active_tokens(farm=div_farm, opposite_farm=sb_pool, day=day, freeze_period=freeze_period)
            continue

        # Count dividends / (number of tokens) for both farms
        ratio_div_farm = div_div_farm / num_tokens_div_farm
        ratio_sb_pool = div_sb_pool / num_tokens_sb_pool

        # Transfer all active tokens of investor to a more profitable farm
        if ratio_div_farm > ratio_sb_pool:
            investor.transfer_active_tokens(farm=div_farm, opposite_farm=sb_pool, day=day,  freeze_period=freeze_period)
            continue
        else:
            investor.transfer_active_tokens(farm=sb_pool, opposite_farm=div_farm, day=day, freeze_period=freeze_period)
            continue


def pay_dividends(dict_investors: dict, farm: Farm, day: int):

    # Calculate dividends per token
    num_tokens = farm.get_tokens_amount(day=day)
    num_dividends = farm.get_current_dividends(day=day)
    dividends_per_token = num_dividends / num_tokens

    for group in dict_investors:
        investors = dict_investors[group]
        for investor in investors:
            num_dividends_investor = investor.get_tokens_amount(farm=farm, day=day) * dividends_per_token
            params_dividends_tokens = {'Staking rewards': num_dividends_investor}
            investor.add_tokens(params_tokens=params_dividends_tokens, day=day)










