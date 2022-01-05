import pandas as pd
import numpy as np
from preprocessing.prepare_config_files import prepare_token_params_sample, prepare_initial_params_sample
from utilities.py_tools import log
from models.investors import Investor
from models.farms import Farm


# Read DataFrame with initial Params
df_initial_params = prepare_initial_params_sample()

# Params for risk coefficient distribution
MU, SIGMA = float(df_initial_params['risk_mu'].values[0]), float(df_initial_params['risk_std'].values[0])

# Number of investors
NUM_INVESTORS = int(df_initial_params['investors_num'].values[0])

# Turnover parameters
TURNOVER, TURNOVER_RATE = float(df_initial_params['turnover'].values[0]), float(df_initial_params['turnover_rate'].values[0])


investor = Investor(risk_coefficient=0.1, months_num=48)
sb_pool = Farm()
log("Token params sample is loaded")
