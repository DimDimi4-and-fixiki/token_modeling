import pickle
import gc
from datetime import datetime
import json
import logging

import numpy
import pandas as pd
import numpy as np
import sys
from time import time
import functools
from bisect import bisect_left
from pathlib import Path
import os
import utilities
from dotenv import load_dotenv

sys.modules['utilities'] = utilities
load_dotenv()


def get_root():

    current_path = str(Path.cwd()).replace("\\", "/")
    # Gets root path to the directory of the project
    if int(os.getenv('LOCAL_DEBUG')):
        return current_path + '/'
    else:
        return '/'.join(current_path.split('/')) + '/../'


def log(to_print):
    """
    Like print, but also prints datetime. Will be made more difficult if saving to log files is needed
    :param to_print: text for printing
    :return: True
    """
    print(datetime.now().strftime('%H:%M:%S.%f')[:-4], to_print)
    return True


def read_file(file_name, root=get_root(), encoding='cp1251', usecols=None, dtype=None, sep=',',
              sheetname=0, skiprows=None, nrows=None, header = 0, names = None, index_col=None, quotechar='\"', df_name='df', verbose=False):
    if file_name.endswith(".csv") | file_name.endswith(".zip"):
        df = pd.read_csv(root + file_name, encoding=encoding, dtype=dtype, sep=sep, names=names,
                         usecols=usecols, error_bad_lines=False, nrows=nrows, index_col=index_col, quotechar=quotechar
                         )
        if verbose:
            log('Loaded ' + file_name)
        return df
    elif file_name.endswith(".txt"):
        df = pd.read_csv(root + file_name, encoding=encoding, dtype=dtype, sep=sep, header=header,
                         usecols=usecols, error_bad_lines=False, nrows=nrows)
        if verbose:
            log('Loaded ' + file_name)
        return df
    elif file_name.endswith(".xlsx") | file_name.endswith(".xls"):
        df = pd.read_excel(root + file_name, dtype=dtype, header=header, nrows=nrows, index_col=index_col,
                           sheet_name=sheetname, skiprows=skiprows, engine='openpyxl')
        if names is not None:
            df.dropna(how='all', axis=1, inplace=True)
            df.columns = names
        if usecols is not None:
            df = df[usecols]
        if verbose:
            log('Loaded ' + file_name)
        return df
    elif file_name.endswith('.hd5'):
        if verbose:
            log('Loaded ' + file_name)
        return pd.read_hdf(root + file_name, key=df_name)
    else:
        file_name = file_name + '.csv'
        df = pd.read_csv(root + file_name, encoding=encoding, dtype=dtype, sep=sep,
                         usecols=usecols, error_bad_lines=False, nrows=nrows, index_col=index_col, quotechar=quotechar)
        if verbose:
            log('Loaded ' + file_name)
        return df


def save_file(file_name, data, root=get_root(), encoding='cp1251', sep=',', sheetname=0,
              header=0,  df_name='df', index=False, verbose=False):

    # Check if directory exists
    os.makedirs(os.path.dirname(root + file_name), exist_ok=True)

    if file_name.endswith(".csv"):
        data.to_csv(root + file_name, encoding=encoding, sep=sep, index=index)
        if verbose:
            log('Loaded ' + file_name)

    elif file_name.endswith(".txt"):
        with open(root + file_name, 'w', encoding=encoding) as f:
            f.write(data)
        if verbose:
            log('Loaded ' + file_name)

    elif file_name.endswith(".xlsx") | file_name.endswith(".xls"):
        data.to_excel(root + file_name, header=header, sheet_name=sheetname)
        if verbose:
            log('Loaded ' + file_name)

    elif file_name.endswith('.hd5'):
        data.to_hdf(root + file_name, key=df_name)
        if verbose:
            log('Loaded ' + file_name)
    else:
        file_name = file_name + '.csv'
        data.read_csv(root + file_name, encoding=encoding, sep=sep, index=index)
        if verbose:
            log('Loaded ' + file_name)


def get_turnover_distribution(turnover, turnover_rate, num_years, growth_type='linear'):
    """

    :param turnover: Initial turnover
    :param turnover_rate: Annual rate of turnover growth
    :param num_years: Number of years to get distribution for
    :param growth_type: Type of distribution
    """

    # Distribution of the turnover
    turnover_distr = [turnover]
    num_days = 365 * num_years

    for num_year in range(1, num_years + 1):
        turnover_prev_year = turnover * (1 + turnover_rate) ** (num_year - 1)
        turnover_next_year = turnover * (1 + turnover_rate) ** num_year
        turnover_delta = (turnover_next_year - turnover_prev_year) / 365

        for num_day in range(1, 366):
            turnover_distr.append(turnover_prev_year + num_day * turnover_delta)

    return turnover_distr


def get_distribution_by_sum(sum: int, size: int):

    # Generate random distribution with .sum() ~= sum
    l = numpy.ones(size)
    distr = np.random.dirichlet(l)
    distr *= sum
    distr = np.round(distr, 0)
    distr = distr.astype(int)

    # Add +1 or -1 to the elements to get needed sum
    delta = abs(sum - distr.sum())
    indexes = numpy.random.randint(size, size=delta)

    for index in indexes:
        if distr.sum() < sum:
            distr[index] += 1
        elif distr.sum() < sum:
            distr[index] -= 1
    return distr


def get_month_by_day(day: int) -> int:
    """
    Gets month number by a day number, months start from zero
    :param day: number of the day
    """
    if day == 0:
        return 0
    else:
        return (day - 1) // 30
