"""
Module with data analysis routines.
"""

import os
import pandas as pd
import numpy as np
from scipy import integrate
from scipy import constants

import logging

from nmran import common
from nmran import dataio
from nmran import datavis


def show_dir_fft(path):
    dataobjs = dataio.loaddir(path)
    dv = datavis.data_viewer()
    for fname, dataobj in dataobjs.iteritems():
        ft = fft(dataobj)
        dv.add_object(ft, fname)
    return dv


def show_dir(path):
    """Loads all known file formats in the specfied directory
    and launches data viewer.
    """
    dataobjs = dataio.loaddir(path)
    dv = datavis.data_viewer()
    for fname, dataobj in dataobjs.iteritems():
        dv.add_object(dataobj, fname)
    return dv


def fft(fid, header=0, footer=0):
    """Returns complex valued FFT of input signal as DataFrame object.

    Frequencies in Hz are index of the returned DataFrame.
    """
    logging.debug('computing FFT of input signal of length: {}'
                  .format(len(fid)))

    fid_input = fid['Re'] + fid['Im'] * 1j
    fft_output = np.fft.fft(fid_input)
    fft_output = np.fft.fftshift(fft_output)
    fft_freqs = np.fft.fftfreq(
        len(fid_input), (fid_input.index[1] - fid_input.index[0]) * 1e-6)
    fft_freqs = np.fft.fftshift(fft_freqs)
    return pd.DataFrame(fft_output, index=fft_freqs, columns=['fft'])


def integrate_fft(input_fft):
    """Integrates given FFT input signal."""
    try:
        return integrate.simps(np.abs(input_fft)['fft'],
                               input_fft.index)
    except Exception as e:
        raise ValueError('Failed to integrate provided input FFT.', e)


def water_term_pol(B0, T):
    gamma = constants.value('proton gyromag. ratio')
    hbar = constants.hbar
    k = constants.k

    larmor_w = gamma * B0
    pol = hbar * larmor_w
    pol /= (2 * k * T)
    return pol


def zeropad(fid, zeros_num=None):
    """Pad signal with specified amount of zeros.

    Args:
      fid (DataFrame): Pandas dataframe with FID.
      zeros_num (int): Amount of zeros to pad with.
        If this argument is None, then it will be 3 * len(fid).
    Returns:
      New DataFrame object with padded zeros.
    """
    if len(fid) < 2:
        raise(ValueError(('Invalid input FID signal: {}. '
                         'Its length should be at least 2.')
                         .format(fid)))
    if zeros_num is None:
        zeros_num = len(fid) * 3
    idx = []
    max_idx = len(fid) - 1
    dwell = fid.index[1] - fid.index[0]
    for i in range(zeros_num):
        idx.append(max_idx + (i + 1) * dwell)
    df = pd.DataFrame(0, index=idx, columns=fid.columns)
    return fid.append(df)


def naph_pol(fid):
    """Returns polarization signal from naphthalene FID in a.u."""
    return integrate_fft(fft(fid))


def _configure_logging():
    program_path = os.path.dirname(os.path.realpath(__file__))
    logging.config.fileConfig(os.path.join(program_path, 'logging.cfg'))


if __name__ == '__main__':
    common.configure_logging()
