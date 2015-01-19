"""
Module with data analysis routines.
"""

import os
import sys
import pandas as pd
import numpy as np
from scipy import constants, integrate

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


def fft(fid, dwell=1e-6, header=0, footer=0):
    """Returns complex valued FFT of input signal as DataFrame object.

    Frequencies in Hz are index of the returned DataFrame.
    """
    logging.debug('computing FFT of input signal of length: {}'
                  .format(len(fid)))
    fft_output = np.fft.fft(fid)
    fft_output = np.fft.fftshift(fft_output)
    fft_freqs = np.fft.fftfreq(len(fid), dwell * 1e-6)
    fft_freqs = np.fft.fftshift(fft_freqs)
    return (fft_freqs, fft_output)


def auto_phase_correct(input_signal, signal_args, step=5):
    logging.debug('searching phase correction angle:')
    logging.debug('\t - on an input signal of length: {}'
                  .format(len(input_signal)))
    logging.debug('\t - with angle step: {}'.format(step))
    assert(len(input_signal) == len(signal_args))
    res = []
    theta = 0
    while theta <= 360:
        signal_pc = phase_correct(input_signal, angle=theta)
        abs_int = integrate.simps(np.real(signal_pc), signal_args)
        disp_int = integrate.simps(np.imag(signal_pc), signal_args)
        res.append((theta, abs_int, disp_int))
        theta += step
    min_disp = sys.maxint
    pc_idx = 0
    for idx, (theta, abs_int, disp_int) in enumerate(res):
        if abs(disp_int) < min_disp and abs_int > 0:
            min_disp, pc_idx = abs(disp_int), idx
    logging.debug(('found angle: {};\n'
                   '\t - dispersive part integrand: {} \n'
                   '\t - absorptive part integrand: {}')
                  .format(res[pc_idx][0], res[pc_idx][2], res[pc_idx][1]))
    return (res[pc_idx][0], phase_correct(input_signal, angle=res[pc_idx][0]))


def phase_correct(input_signal, angle=0):
    a = np.radians(angle)
    re, im = np.real(input_signal), np.imag(input_signal)
    absorptive = re * np.cos(a) + im * np.sin(a)
    dispersive = re * -np.sin(a) + im * np.cos(a)
    return absorptive + dispersive * 1j


def weight_signal(x, y, lb=1.0):
    """Multiplies input FID by an exponential window: exp(...)."""
    return y * _compute_exp_window(x, y, lb=lb)
    

def _compute_exp_window(x, y, lb=1.0):
    """Returns an exponential window for passed signal."""
    assert(len(x) == len(y))
    exp_args = np.arange(1, len(x) + 1)
    exp_mul = np.exp(- lb * exp_args / float(len(x)))
    return exp_mul


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


def _configure_logging():
    program_path = os.path.dirname(os.path.realpath(__file__))
    logging.config.fileConfig(os.path.join(program_path, 'logging.cfg'))


if __name__ == '__main__':
    common.configure_logging()
