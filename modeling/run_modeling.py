"""
    0. Imports of modules
"""

import pandas as pd
import numpy as np
from preprocessing.prepare_config_files import prepare_token_params_sample, prepare_initial_params_sample, prepare_mint_sample
from utilities.py_tools import log, get_turnover_distribution
from models.investors import Investor
from models.farms import Farm
from utilities.modelling_tools import create_investors, sell_tokens, get_mint_distribution_by_month


"""
    1. Constants for modelling
"""

# Read DataFrame with initial Params
df_initial_params = prepare_initial_params_sample()
df_mint_distr = prepare_mint_sample()

# Params for risk coefficient distribution
MU, SIGMA = float(df_initial_params['risk_mu'].values[0]), float(df_initial_params['risk_std'].values[0])

# Number of months and years to run modelling
NUM_MONTHS = int(df_initial_params['months_num'].values[0])
NUM_YEARS = NUM_MONTHS // 12 + 1

# Modelling parameters dictionary
PARAMS_MODELLING = {
    'num_months': NUM_MONTHS,
    'mu': MU,
    'sigma': SIGMA
}

# Number of investors for different types
NUM_INVESTORS_SEED = int(df_initial_params['investors_seed_num'].values[0])
NUM_INVESTORS_PRIVATE_SALE = int(df_initial_params['investors_private_sale_num'].values[0])
NUM_INVESTORS_PUBLIC_SALE = int(df_initial_params['investors_public_sale_num'].values[0])
NUM_INVESTORS_TEAM = int(df_initial_params['investors_team_num'].values[0])
NUM_INVESTORS_COMMUNITY = int(df_initial_params['investors_community_num'].values[0])


PARAMS_INVESTORS = {
    'Seed': NUM_INVESTORS_SEED,
    'Private sale': NUM_INVESTORS_PRIVATE_SALE,
    'Public sale': NUM_INVESTORS_PUBLIC_SALE,
    'Team': NUM_INVESTORS_TEAM,

    # todo: Community investors are not included now
    # 'Community': NUM_INVESTORS_COMMUNITY,
}

# Turnover parameters
TURNOVER, TURNOVER_RATE = float(df_initial_params['turnover'].values[0]), float(df_initial_params['turnover_rate'].values[0])

# Percent of turnover that is paid as dividends
PERCENT_DIVIDENDS = float(df_initial_params['dividends_percent'].values[0])

# Distribution of the turnover
TURNOVER_DISTRIBUTION = get_turnover_distribution(turnover=TURNOVER, turnover_rate=TURNOVER_RATE, num_years=NUM_YEARS)


# Number of tokens in SbPool
NUM_SEED_TOKENS_SB_POOL = int(df_initial_params['tokens_seed_num_sb_pool'].values[0])
NUM_COMMUNITY_TOKENS_SB_POOL = int(df_initial_params['tokens_community_num_sb_pool'].values[0])

# Token parameters for SbPool
PARAMS_TOKENS_SB_POOL = {
    'Seed': NUM_SEED_TOKENS_SB_POOL,
    'Community': NUM_COMMUNITY_TOKENS_SB_POOL
}

# Initialize Sb Pool object with Seed and Community tokens
sb_pool = Farm()
sb_pool.add_tokens(params_tokens=PARAMS_TOKENS_SB_POOL, day=1)

# State of the system: 1, 2 or 3
state = 1

# Get dictionary with Investor objects for all groups
investors = create_investors(PARAMS_INVESTORS, PARAMS_MODELLING)

# Tokens that we are not modelling now
TOKENS_EXCLUDED = ['Staking rewards', 'Community']

for num_month in range(0, NUM_MONTHS + 1):
    # Get tokens that would be released during the current month
    params_tokens = get_mint_distribution_by_month(mint_distr=df_mint_distr, num_month=num_month)

    # In a month = 0, we put some tokens in SbPool
    if num_month == 0:
        # Take away tokens that are put in SbPool
        params_tokens['Seed'] -= NUM_SEED_TOKENS_SB_POOL
        params_tokens['Community'] -= NUM_COMMUNITY_TOKENS_SB_POOL

    # todo: Get mint distribution by days in a month
    for day in range(1, 30 + 1):
        # todo: for each day share tokens between investors
        pass


sell_tokens(investors=investors, params_tokens=params_tokens, day=1)
sb_pool.update(day=1)

log("Token params sample is loaded")
