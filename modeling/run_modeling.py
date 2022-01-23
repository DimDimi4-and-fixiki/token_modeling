"""
    0. Imports of modules
"""

import pandas as pd
import numpy as np
from preprocessing.prepare_config_files import prepare_token_params_sample, prepare_initial_params_sample, prepare_mint_sample
from utilities.py_tools import log, get_turnover_distribution
from models.farms import Farm
from utilities.modelling_tools import create_investors, sell_tokens, get_mint_distribution_by_month, \
    distribute_tokens_by_days, get_tokens_distribution_by_day, transfer_investors, pay_dividends
from tqdm import tqdm

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

MIN_INDEX_REVENUE = float(df_initial_params['min_revenue_index'].values[0])

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

# Periods of extra mint and dividends payments
PERIOD_EXTRA_MINT = int(df_initial_params['extra_mint_period'].values[0])
PERIOD_DIVIDENDS = int(df_initial_params['dividends_period'].values[0])

# Distribution of the turnover
TURNOVER_DISTRIBUTION = get_turnover_distribution(turnover=TURNOVER, turnover_rate=TURNOVER_RATE, num_years=NUM_YEARS)

# Currency rates
RATE_USD_BNB = float(df_initial_params['dollar_bnb_ratio'])
RATE_BNB_SMARTY = float(df_initial_params['bnb_smarty_ratio'])

# Number of tokens in SbPool
NUM_SEED_TOKENS_SB_POOL = int(df_initial_params['tokens_seed_num_sb_pool'].values[0])
NUM_COMMUNITY_TOKENS_SB_POOL = int(df_initial_params['tokens_community_num_sb_pool'].values[0])

# Token parameters for SbPool
PARAMS_TOKENS_SB_POOL = {
    'Seed': NUM_SEED_TOKENS_SB_POOL,
    'Community': NUM_COMMUNITY_TOKENS_SB_POOL
}


# Tokens that we are not modelling now
TOKENS_EXCLUDED = ['Community', 'Staking rewards']


"""
    2. Initialize farms and investors 
"""

# Initialize Sb Pool object with Seed and Community tokens
sb_pool = Farm(type='SbPool', params_tokens=PARAMS_TOKENS_SB_POOL)
sb_pool.add_tokens(params_tokens=PARAMS_TOKENS_SB_POOL, day=1, currency_rate=RATE_BNB_SMARTY)

# Create Div Farm pool object
div_farm = Farm(type='DivFarm')


# Get dictionary with Investor objects for all groups
investors = create_investors(PARAMS_INVESTORS, PARAMS_MODELLING)


"""
    3. Define extra parameters for keeping statistics
"""

cols_currency_rate = ['Day', 'BNB / Smarty Rate']
df_currency_rate = pd.DataFrame(columns=cols_currency_rate)

cols_turnover = ['Day', 'Shop Turnover, Smarty']
df_turnover = pd.DataFrame(columns=cols_turnover)

"""
    4. Run modelling
"""

for num_month in range(0, 2):

    log(f'----- Modeling for month = {num_month} started -----')

    # Get tokens that would be released during the current month
    params_tokens = get_mint_distribution_by_month(mint_distr=df_mint_distr, num_month=num_month)

    # Delete tokens, which are not included in modelling, from the distribution
    for group in TOKENS_EXCLUDED:
        del params_tokens[group]

    # In a month = 0, we put some tokens in SbPool
    if num_month == 0:

        # Take away tokens that are put in SbPool
        params_tokens['Seed'] -= NUM_SEED_TOKENS_SB_POOL

        # todo: Community tokens are not included now
        # params_tokens['Community'] -= NUM_COMMUNITY_TOKENS_SB_POOL

    distribution_tokens_days = distribute_tokens_by_days(params_tokens)
    for day in tqdm(range(1, 30 + 1)):

        # Calculate number of the day
        num_day = num_month * 30 + day

        # Sell tokens to investors
        distribution_tokens = get_tokens_distribution_by_day(distribution_tokens_days, day)
        sell_tokens(investors=investors, params_tokens=distribution_tokens, day=num_day, excluded_tokens=TOKENS_EXCLUDED)

        # Params for calculating dividends
        sb_pool_rate = 0.5
        div_farm_rate = 1 - sb_pool_rate
        turnover, dividends_rate = TURNOVER_DISTRIBUTION[num_day - 1], 0.3 / 100

        # Convert turnover dividends from USD to Smarty
        bnb_smarty_rate = sb_pool.get_currency_rate(day=day)
        turnover_smarty = turnover / RATE_USD_BNB / bnb_smarty_rate

        df_turnover = df_turnover.append({'Day': day, 'Shop Turnover, Smarty': turnover})

        # Calculate dividends from turnover for each farm
        div_sb_pool = turnover_smarty * dividends_rate * sb_pool_rate
        div_div_farm = turnover_smarty * dividends_rate * div_farm_rate

        # Add dividends to both farms
        div_farm.add_dividends(day=day, num_tokens=div_div_farm, type_dividends='Turnover', type_operation='smarty')
        sb_pool.add_dividends(day=day, num_tokens=div_sb_pool, type_dividends='Turnover', type_operation='smarty')

        # Imitate transfer of tokens by investors
        transfer_investors(sb_pool=sb_pool, div_sb_pool=div_div_farm,
                           div_farm=div_farm, div_div_farm=div_div_farm,
                           dict_investors=investors, day=num_day,
                           freeze_period=10)

        # Mint extra tokens for dividends( if needed)
        if num_day % PERIOD_EXTRA_MINT == 0:

            # Get current BNB / Smarty rate
            bnb_smarty_rate = sb_pool.get_currency_rate(day=day)

            # Mint Smarty tokens to DivFarm
            div_farm.add_dividends(day=day, index_revenue=MIN_INDEX_REVENUE,
                                   type_dividends='Minted', type_operation='index_revenue',
                                   bnb_smarty_rate=bnb_smarty_rate)

            # Mint Smarty tokens to SbPool
            sb_pool.add_dividends(day=day, index_revenue=MIN_INDEX_REVENUE,
                                  type_dividends='Minted', type_operation='index_revenue',
                                  bnb_smarty_rate=bnb_smarty_rate)

        # Pay dividends to investors (if needed)
        if num_day % PERIOD_DIVIDENDS == 0:
            pay_dividends(dict_investors=investors, farm=div_farm, day=day)
            pay_dividends(dict_investors=investors, farm=sb_pool, day=day)

            # Update farms parameters before going to the next day
            sb_pool.update(day=num_day, clear_dividends=True)
            div_farm.update(day=num_day, clear_dividends=True)

        else:
            # Update farms parameters before going to the next day
            sb_pool.update(day=num_day)
            div_farm.update(day=num_day)

        dict_currency_rate = {'Day': day, 'BNB / Smarty Rate': bnb_smarty_rate}
        df_currency_rate = df_currency_rate.append(dict_currency_rate, ignore_index=True)







    print(f'Month {num_month} processed')




log("Token params sample is loaded")
