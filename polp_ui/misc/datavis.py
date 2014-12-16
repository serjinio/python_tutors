

import os
import sys
import pandas as pd
import numpy as np
import pylab
import logging


############################################################
# Data handling
############################################################


KNOWN_FORMATS = ['.dat']


def read(filepath):
    """Loads given data file."""
    if not any(filepath.endswith(fmt) for fmt in KNOWN_FORMATS):
        raise ValueError(('Input file seems to be of unknown format. '
                          'supported formats are: {}'.format(KNOWN_FORMATS)))
    if 'lgr' in filepath and '.dat' in filepath:
        return read_lgr(filepath)


def read_lgr(filepath):
    logging.debug('reading data file: "{}"'.format(filepath))
    if not os.path.exists(filepath):
        raise ValueError('Given file path: "{}" does not exists.'
                         .format(filepath))
    df = pd.read_csv(filepath, sep='\s+', header=None)
    df.columns = ['f', 'Re', 'Im', 'Abs']
    logging.debug('read dataframe: \n{}'.format(df))
    return df


def plot_lgr(filepath):
    df = read_lgr(filepath)
    df.plot('f', 'Re')


if __name__ == '__main__':
    df = None
    if sys.argv[0] and sys.argv[0] != '':
        df = read(sys.argv[0])
