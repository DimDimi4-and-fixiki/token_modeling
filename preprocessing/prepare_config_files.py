import pandas as pd
import logging
from utilities.py_tools import read_file, save_file, get_root

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - [%(levelname)s] (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")


def prepare_mint_sample():

    # Paths for config files
    sample_path = 'config/token_mint_distr.xlsx'

    # Read and clean Data Frame
    try:
        df = read_file(sample_path, encoding='utf8')
        df.fillna(0, inplace=True)
    except (FileNotFoundError, FileExistsError):
        logging.critical(f"Config file in path={sample_path} is not found")
        return

    numeric_columns = df.columns[1:]
    for col in numeric_columns:
        df[col] = df[col].astype('int64')

    return df


def prepare_token_params_sample():
    # Paths for config files
    sample_path = 'config/tokens_params.xlsx'

    # Read config Excel file
    try:
        df = read_file(sample_path, encoding='utf8')
        df.fillna(0, inplace=True)

    except (FileNotFoundError, FileExistsError):
        logging.critical(f"Config file in path={sample_path} is not found")
        return

    return df


def prepare_initial_params_sample(sample_path):
    """
    Reads config file with all constants
    :return: DataFrame with constants
    """

    # Read all Data Frames with constants
    try:

        # Read modelling constants
        df_modelling_constants = read_file(sample_path, encoding='utf8', sheetname='Modelling_Constants')
        df_modelling_constants.drop(df_modelling_constants.filter(regex="Unname"), axis=1, inplace=True)

        # Read dividends constants
        df_dividends_constants = read_file(sample_path, encoding='utf8', sheetname='Dividends_Constants')
        df_dividends_constants.drop(df_dividends_constants.filter(regex="Unname"), axis=1, inplace=True)

        # Read investors constants
        df_investors_constants = read_file(sample_path, encoding='utf8', sheetname='Investors_Constants')
        df_investors_constants.drop(df_investors_constants.filter(regex="Unname"), axis=1, inplace=True)

        # Read SbPool constants
        df_sb_pool_constants = read_file(sample_path, encoding='utf8', sheetname='Sb_Pool_Constants')
        df_sb_pool_constants.drop(df_sb_pool_constants.filter(regex="Unname"), axis=1, inplace=True)

        # Join all Data Frames with constants
        data_frames = [df_modelling_constants, df_sb_pool_constants, df_investors_constants, df_dividends_constants]
        df = pd.concat(data_frames, axis=1)

    except (FileNotFoundError, FileExistsError):
        logging.critical(f"Config file in path={sample_path} is not found")
        return


    # Rename columns
    cols_mapper = {
        'Темп роста оборота в год': 'turnover_rate',
        'Начальный оборот, $': 'turnover',
        'Процент оборота, который выплачивается в виде дивидендов': 'dividends_percent',

        'Начальное число инвесторов типа Seed': 'investors_seed_num',
        'Начальное число инвесторов типа Private Sale': 'investors_private_sale_num',
        'Начальное число инвесторов типа Public Sale': 'investors_public_sale_num',
        'Начальное число инвесторов типа Team': 'investors_team_num',
        'Начальное число инвесторов типа Community': 'investors_community_num',

        # note: Removed as we do not have Stacking Rewards Investors
        # 'Начальное число инвесторов типа Staking Rewards': 'investors_staking_rewards_num',

        'Мат ожидание риска инвестора': 'risk_mu',
        'Стандартное отклонение риска инвестора': 'risk_std',
        'Число месяцев для моделирования': 'months_num',
        'Минимальный порог интереса инвестора': 'min_revenue_index',

        'Начальное число токенов типа Seed в SBPool': 'tokens_seed_num_sb_pool',
        'Начальное число токенов типа Community в SBPool': 'tokens_community_num_sb_pool',

        'Периодичность дочеканивания монет, дней': 'extra_mint_period',
        'Периодичность раздачи дивидендов, дней': 'dividends_period',

        'Начальный Курс BNB / Smarty': 'bnb_smarty_ratio',
        'Начальный Курс $ / BNB': 'dollar_bnb_ratio'
    }
    df.rename(columns=cols_mapper, inplace=True)

    return df


if __name__ == '__main__':
    df_mint_distr = prepare_mint_sample()
    df_token_params = prepare_token_params_sample()
    df_initial_params = prepare_initial_params_sample()
