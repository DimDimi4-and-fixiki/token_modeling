import pandas as pd
import numpy as np
from preprocessing.prepare_config_files import prepare_token_params_sample, prepare_initial_params_sample, prepare_mint_sample
from utilities.py_tools import save_file
from models.farms import Farm
from tqdm import tqdm


def save_results(file_path: str, div_farm: Farm, sb_pool: Farm):

    writer = pd.ExcelWriter(file_path)
    div_farm_tokens = div_farm.tokens.copy(deep=True)
    sb_pool_tokens = sb_pool.tokens.copy(deep=True)

    div_farm_tokens.to_excel(writer, sheet_name='Div_Farm')
    sb_pool_tokens.to_excel(writer, sheet_name='Sb_Pool')

    writer.save()