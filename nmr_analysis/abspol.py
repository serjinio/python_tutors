# analysis of FID signals from water and napthalene protons
#
# Refs:
#   http://www.chem.uzh.ch/teaching/documents/master/che431/NMR.pdf
#   http://physics.wm.edu/physicsnew/undergrad/2003/McGuigan.pdf
#


import os
import pandas as pd
import numpy as np
from scipy import integrate
from scipy import constants

import logging


pd.options.display.mpl_style = 'default'

NMR_SIGNALS_DATA_FOLDER = ('/Users/serj/Dropbox/RIKEN - Spin-isospin '
                           'lab materials/lab data/2013/0719/')
sample_water_signal = ('/Users/serj/projects/polp_data/1209/water-11.smd')
sample_naph_signal = ('/Users/serj/Dropbox/RIKEN - Spin-isospin '
                      'lab materials/lab data/2013/0925/ise44.dat')


############################################################
# Data handling
############################################################


KNOWN_FORMATS = ['.smd', '.dat']


def load(filepath):
    """Loads data file given path."""
    
    if not any(filepath.endswith(fmt) for fmt in KNOWN_FORMATS):
        raise ValueError(('Input file seems to be of unknown format. '
                          'supported formats are: {}'.format(KNOWN_FORMATS)))
        
    if filepath.endswith(KNOWN_FORMATS[0]):
        return _load_smd(filepath)
    elif filepath.endswith(KNOWN_FORMATS[1]):
        return _load_dat(filepath)

        
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
        return integrate.simps(np.abs(input_fft)['fft'], input_fft.index)
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

    
# Private members
############################################################


def _load_smd(filepath):
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
    # calculate abs value for convenience
    df['Abs'] = np.sqrt(df['Re'] ** 2 + df['Im'] ** 2)
    # make up time column (us)
    df['t'] = [dwell * n for n in range(len(df))]
    # index by time
    df = df.set_index('t')

    logging.debug('read dataframe: \n{}'.format(df))
    return df

    
def _load_dat(filepath):
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

    # calculate abs value for convenience
    df['Abs'] = np.sqrt(df['Re'] ** 2 + df['Im'] ** 2)
    # time in us
    df['t'] = df['t'] * 1e6
    # index by time
    df = df.set_index('t')

    logging.debug('read dataframe: \n{}'.format(df))
    return df

    
############################################################
# Misc stuff
############################################################


def configure_logging():
    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)s:  %(message)s')


############################################################
# Main procs
############################################################


# magnetic moments of naphthalene and water
water_mag_moment = 2.7927
# TODO: Find out its magnetic moment, now using for proton
naph_mag_moment = 2.7927
MAG_MOMENT_RATIO = water_mag_moment / naph_mag_moment

# difference in protons number of water and 6He samples:
# this one assumes that samples are equal in volume
# n_w / n_6He
# water_n_protons = np.pi * 14e-3 ** 2 * 1e4 * 3.01e22 * 2 / 3.
# naph_n_protons = np.pi * 14e-3 ** 2 * 1e4 * 2.89e22 * 8 / 18.
# N_RATIO = water_n_protons / naph_n_protons

# this one assumes that samples with equal amount of protons
N_RATIO = 1.

# electronic gain difference during water and signals 6He acquisition
# G_w / G_naph
# PAmp + main_amp [dB]
G_w = 30. + 80.
# just main_amp [dB]
G_naph = 70.
ELECTRONIC_GAIN_RATIO = 10 ** ((G_w - G_naph) / 20.)

# water thermal pol
WATER_POL = water_term_pol(0.1, 295)

# small spin flip during naph pol. measurement [deg]
SMALL_SPIN_FLIP = 4.78


def get_abs_pol():
    water, naph = load(sample_water_signal), load(sample_naph_signal)

    # polarization ration between naph and water: S_6He / S_w
    naph = naph * (1 / np.sin(np.radians(SMALL_SPIN_FLIP)))
    water_fft, naph_fft = fft(water[850:]), fft(naph[1100:])
    pol_ratio = integrate_fft(naph_fft) / integrate_fft(water_fft)

    # 6He polarization
    full_pol_ratio = MAG_MOMENT_RATIO * N_RATIO * \
        ELECTRONIC_GAIN_RATIO * pol_ratio
    abs_pol = WATER_POL * full_pol_ratio * 100
    
    return full_pol_ratio, abs_pol

    
if __name__ == '__main__':
    configure_logging()

    print 'Samples summary (water / naph): '
    print '  Magnetic moments ratio: {:.2f}'.format(MAG_MOMENT_RATIO)
    print '  # protons ratio: {:.2f}'.format(N_RATIO)
    print '  electronic gain ratio: {:.2f}'.format(ELECTRONIC_GAIN_RATIO)
    print ('  Naphthalene spin flip angle (a): {:.2f} '
           '[deg] (1/sin(a): {:.2f})').format(
               SMALL_SPIN_FLIP, 1 / np.sin(np.radians(SMALL_SPIN_FLIP)))
    
    pol_ratio, abs_pol = get_abs_pol()
    print 'Polarization:'
    print '  Polarization ratio of naph vs water: {:.2f}' \
        .format(pol_ratio)
    print '  Napthalene polarization = {:.4f} %'.format(abs_pol)

    water, naph = load(sample_water_signal), \
        load(sample_naph_signal)
    naph = naph * (1 / np.sin(np.radians(SMALL_SPIN_FLIP)))
    water_fft, naph_fft = fft(water), fft(naph)

