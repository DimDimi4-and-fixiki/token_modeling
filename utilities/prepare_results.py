from datetime import datetime

import pandas as pd
import numpy as np
from preprocessing.prepare_config_files import prepare_token_params_sample, prepare_initial_params_sample, prepare_mint_sample
from utilities.py_tools import save_file
from models.farms import Farm
from tqdm import tqdm


def save_results(folder_path: str, div_farm: Farm, sb_pool: Farm, df_currency_rate: pd.DataFrame,
                 df_turnover: pd.DataFrame):

    # Initialize Excel Writer
    current_time = datetime.now().strftime("%Y%m%d-%H%M%S").replace('-', '_')
    file_name = f'results_{current_time}.xlsx'
    file_path = folder_path + file_name
    writer = pd.ExcelWriter(file_path)

    """
        Step 1. Get all statistics
    """
    # Get tokens statistics
    div_farm_tokens = div_farm.tokens.copy(deep=True).transpose()
    sb_pool_tokens = sb_pool.tokens.copy(deep=True).transpose()

    # Get dividends statistic
    div_farm_dividends = div_farm.dividends.copy(deep=True).transpose()
    sb_pool_dividends = sb_pool.dividends.copy(deep=True).transpose()

    """
        Step 2. Save tables in Excel sheets
    """
    # Save tokens stats to Excel
    div_farm_tokens.to_excel(writer, sheet_name='Div_Farm')
    sb_pool_tokens.to_excel(writer, sheet_name='Sb_Pool')

    # Save dividends stats to Excel
    div_farm_dividends.to_excel(writer, sheet_name='Dividends_Div_Farm')
    sb_pool_dividends.to_excel(writer, sheet_name='Dividends_Sb_Pool')

    df_currency_rate.to_excel(writer, sheet_name='Currency_Rate')
    df_turnover.to_excel(writer, sheet_name='Shop_Turnover')

    writer.save()