'''
STEVEN UNIVERSE: Scrape Steven Universe Wiki and analyze transcripts

Author: Charmaine Runes

This file loads CSV files into pandas dataframes and cleans the data.
'''

import pandas as pd
import numpy as np
import csv


def load_data(filename):
    '''
    Takes a filename and returns a pandas dataframe
    '''

    df = pd.read_csv(filename)

    return df
