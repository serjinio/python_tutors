"""
Module with read & write procedures for datasets.
"""


import os
import pandas as pd
import numpy as np
import logging

import common


KNOWN_FORMATS = ['.smd', '.dat']


def loaddir(path):
    """Loads all known file formats in the specfied directory. """
    files = listdir(path)
    dataobjs = {}
    logging.debug('loading all data files from "{}"'
                  .format(path))
    for f in files:
        dataobjs[os.path.basename(f)] = load(f)
    return dataobjs


def listdir(path):
    files = [f for f in os.listdir(path) if
             os.path.isfile(os.path.join(path, f))]
    known_files = []
    for f in files:
        for ext in KNOWN_FORMATS:
            if f.endswith(ext):
                known_files.append(os.path.join(path, f))
                continue
    return known_files


def load(filepath):
    """General purpose load procedure for datasets of different formats."""
    
    if not any(filepath.endswith(fmt) for fmt in KNOWN_FORMATS):
        raise ValueError(('Input file seems to be of unknown format. '
                          'supported formats are: {}'.format(KNOWN_FORMATS)))
        
    if filepath.endswith(KNOWN_FORMATS[0]):
        return load_smd(filepath)
    elif filepath.endswith(KNOWN_FORMATS[1]):
        return load_dat(filepath)


def load_smd(filepath):
    logging.debug('reading data file: "{}"'.format(filepath))
    if not os.path.exists(filepath):
        raise ValueError('Given file path: "{}" does not exists.'
                         .format(filepath))
        
    df = pd.read_csv(filepath, sep='\s+', header=4)

    # header params
    with file(filepath, 'rb') as input_file:
        npoints, dwell, sf1 = [input_file.readline()
                               for i in range(0, 3)]
    npoints, dwell, sf1 = int(npoints[6:]), float(dwell[3:]), float(sf1[4:])
    logging.debug('header data: npoints={}; dwell={}, sf1={}'
                  .format(npoints, dwell, sf1))
    
    # name
    df.columns = ['Re', 'Im']
    # make up time column (us)
    df['t'] = [dwell * n for n in range(len(df))]
    # index by time
    df = df.set_index('t')

    logging.debug('read dataframe of length: {}'.format(len(df)))
    return df

    
def load_dat(filepath):
    logging.debug('reading data file: "{}"'.format(filepath))
    if not os.path.exists(filepath):
        raise ValueError('Given file path: "{}" does not exists.'
                         .format(filepath))
        
    df = pd.read_csv(filepath, sep='\s+', header=None, skipfooter=5)

    # remove unnecessary columns
    del df[5]
    del df[4]
    del df[3]
        
    # name
    df.columns = ['t', 'Re', 'Im']
    # time in us
    df['t'] = df['t'] * 1e6
    # index by time
    df = df.set_index('t')

    logging.debug('read dataframe of length: {}'.format(len(df)))
    return df


if __name__ == '__main__':
    common.configure_logging()
