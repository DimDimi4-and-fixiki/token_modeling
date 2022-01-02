import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)


def prepare_mint_sample():

    # Paths for config files
    sample_path = '../config/token_mint_distr.xlsx'
    result_path = '../config/token_mint_distr.csv'

    # Read and clean Data Frame
    try:
        df = pd.read_excel(sample_path)
        df.fillna(0, inplace=True)
    except (FileNotFoundError, FileExistsError):
        logging.critical(f"Config file in path={sample_path} is not found")
        return

    # Save and return the result
    df.to_csv(result_path, encoding='utf8')
    return df


def prepare_token_params_sample():
    # Paths for config files
    sample_path = '../config/tokens_params.xlsx'
    result_path = '../config/token_params.csv'

    # Read config Excel file
    df = pd.read_excel(sample_path)
    df.fillna(0, inplace=True)

    # Save result as csv file
    df.to_csv(result_path, encoding='utf8')


if __name__ == '__main__':
    df = prepare_mint_sample()
