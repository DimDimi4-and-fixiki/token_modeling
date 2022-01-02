import pandas as pd
import logging

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - [%(levelname)s] (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")


def prepare_mint_sample():

    # Paths for config files
    sample_path = 'config/token_mint_distr.xlsx'
    result_path = 'config/token_mint_distr.csv'

    # Read and clean Data Frame
    try:
        df = pd.read_excel(sample_path)
        df.fillna(0, inplace=True)
    except (FileNotFoundError, FileExistsError):
        logging.critical(f"Config file in path={sample_path} is not found")
        return

    # Save and return the result
    df.to_csv(result_path, encoding='utf8', index=False)
    return df


def prepare_token_params_sample():
    # Paths for config files
    sample_path = 'config/tokens_params.xlsx'
    result_path = 'config/token_params.csv'

    # Read config Excel file
    try:
        df = pd.read_excel(sample_path)
        df.fillna(0, inplace=True)

    except (FileNotFoundError, FileExistsError):
        logging.critical(f"Config file in path={sample_path} is not found")
        return

    # Save result as csv file
    df.to_csv(result_path, encoding='utf8', index=False)
    return df


if __name__ == '__main__':
    df_mint_distr = prepare_mint_sample()
    df_token_params = prepare_token_params_sample()
