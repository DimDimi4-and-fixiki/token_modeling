import pandas as pd
import logging
from utilities.py_tools import read_file, save_file, get_root

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - [%(levelname)s] (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")


def prepare_mint_sample():

    # Paths for config files
    sample_path = 'config/token_mint_distr.xlsx'
    result_path = 'config/token_mint_distr.csv'

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

    # Save and return the result
    save_file(result_path, df, encoding='utf8')
    return df


def prepare_token_params_sample():
    # Paths for config files
    sample_path = 'config/tokens_params.xlsx'
    result_path = 'config/token_params.csv'

    # Read config Excel file
    try:
        df = read_file(sample_path, encoding='utf8')
        df.fillna(0, inplace=True)

    except (FileNotFoundError, FileExistsError):
        logging.critical(f"Config file in path={sample_path} is not found")
        return

    # Save result as csv file
    save_file(result_path, df, encoding='utf8', index=False)
    return df


def prepare_initial_params_sample():
    # Paths for config files
    sample_path = 'config/initial_params.xlsx'
    result_path = 'config/token_params.csv'

    # Read config Excel file
    try:
        df = read_file(sample_path, encoding='utf8')
        df.fillna(0, inplace=True)

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

        'Начальное число токенов типа Seed в SBPool': 'tokens_seed_num_sb_pool',
        'Начальное число токенов типа Community в SBPool': 'tokens_community_num_sb_pool',

        'Периодичность дочеканивания монет, дней': 'extra_mint_period',
        'Периодичность раздачи дивидендов, дней': 'dividends_period'
    }
    df.rename(columns=cols_mapper, inplace=True)

    # Save result as csv file
    # save_file(result_path, df, encoding='utf8', index=False)
    return df


if __name__ == '__main__':
    df_mint_distr = prepare_mint_sample()
    df_token_params = prepare_token_params_sample()
    df_initial_params = prepare_initial_params_sample()
    print('k')
