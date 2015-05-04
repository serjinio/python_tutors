

import os

import numpy as np
import pandas as pd
from scipy import integrate
from scipy import constants

from nmran.analyse import fft, zeropad, phase_correct, \
    weight_signal, auto_phase_correct
from nmran.dataio import load
from nmran.datavis import data_viewer
from nmran import common


FID_EXP_WEIGHTING = 15.

# this one assumes that samples with equal amount of protons
N_RATIO = 1.

# fraction of target sample area irradiated by laser light
# IRRADIATION_FACTOR_2014 = 10 ** 2 / 12. ** 2
IRRADIATION_FACTOR_2014 = 1.


def water_term_pol(B0, T):
    gamma = constants.value('proton gyromag. ratio')
    hbar = constants.hbar
    k = constants.k

    larmor_w = gamma * B0
    pol = hbar * larmor_w
    pol /= (2 * k * T)
    return pol

    
WATER_DATA_DIR = '/Users/serj/projects/polp_data/1211/'
WATER_FID = {'data': 'water-14.smd', 'gain': 100, 'pc': 240}
WATER_POL = water_term_pol(0.1, 295)
# Setup-specific correction for water signal.
# In this case ratio of signals from bottle to signal from
# reference sponge as we cannot get signal with
# necessarily short decay time from sponge - it is too weak.
WATER_SIGNAL_CORRECTION_FACTOR = 0.1535
# WATER_SIGNAL_CORRECTION_FACTOR = 1.


data2014_dir = '/Users/serj/projects/polp_data/1225/'
small_flip_angle2014 = 7.55
buildup2014_fids = [
    {'data': 'ise15.dat', 'gain': 80, 'pc': 240, 't': 0},
    {'data': 'ise16.dat', 'gain': 80, 'pc': 240, 't': 30},
    {'data': 'ise19.dat', 'gain': 80, 'pc': 240, 't': 50},
    {'data': 'ise22.dat', 'gain': 80, 'pc': 240, 't': 70},
    {'data': 'ise24.dat', 'gain': 80, 'pc': 240, 't': 90},
    {'data': 'ise26.dat', 'gain': 80, 'pc': 240, 't': 120},
    {'data': 'ise28.dat', 'gain': 80, 'pc': 240, 't': 150},
    {'data': 'ise30.dat', 'gain': 80, 'pc': 240, 't': 180},
    {'data': 'ise32.dat', 'gain': 80, 'pc': 240, 't': 290},
    {'data': 'ise40.dat', 'gain': 50, 'pc': 285, 't': 320},
    {'data': 'ise41.dat', 'gain': 50, 'pc': 285, 't': 350},
    {'data': 'ise42.dat', 'gain': 50, 'pc': 285, 't': 380}
]


data2013_dir = '/Users/serj/projects/polp_data/2013/0925/'
small_flip_angle2013 = 4.75
buildup2013_fids = [
    {'data': 'ise7.dat', 'gain': 70, 'pc': 345, 't': 15},
    {'data': 'ise8.dat', 'gain': 70, 'pc': 345, 't': 30},
    {'data': 'ise9.dat', 'gain': 70, 'pc': 345, 't': 45},
    {'data': 'ise10.dat', 'gain': 70, 'pc': 345, 't': 60},
    {'data': 'ise11.dat', 'gain': 70, 'pc': 345, 't': 75},
    {'data': 'ise12.dat', 'gain': 70, 'pc': 345, 't': 90},
    {'data': 'ise14.dat', 'gain': 70, 'pc': 345, 't': 105},
    {'data': 'ise17.dat', 'gain': 70, 'pc': 345, 't': 120},
    {'data': 'ise19.dat', 'gain': 70, 'pc': 345, 't': 135},
    {'data': 'ise21.dat', 'gain': 70, 'pc': 345, 't': 150},
    {'data': 'ise22.dat', 'gain': 70, 'pc': 345, 't': 165},
    {'data': 'ise24.dat', 'gain': 70, 'pc': 345, 't': 180},
    {'data': 'ise26.dat', 'gain': 70, 'pc': 345, 't': 195},
    {'data': 'ise28.dat', 'gain': 70, 'pc': 345, 't': 210},
    {'data': 'ise30.dat', 'gain': 70, 'pc': 345, 't': 225},
    {'data': 'ise32.dat', 'gain': 70, 'pc': 345, 't': 240},
    {'data': 'ise34.dat', 'gain': 70, 'pc': 345, 't': 270},
    {'data': 'ise35.dat', 'gain': 70, 'pc': 345, 't': 300},
    {'data': 'ise36.dat', 'gain': 70, 'pc': 345, 't': 360},
    {'data': 'ise38.dat', 'gain': 70, 'pc': 345, 't': 420},
    {'data': 'ise40.dat', 'gain': 70, 'pc': 345, 't': 480},
    {'data': 'ise42.dat', 'gain': 70, 'pc': 345, 't': 540},
    {'data': 'ise44.dat', 'gain': 70, 'pc': 345, 't': 600},
    {'data': 'ise46.dat', 'gain': 70, 'pc': 345, 't': 660},
]


def process_fid(fid):
    ft = cut_fft(do_fft(cut_fid(fid)))
    res = integrate.simps(np.real(ft['fft']),
                          ft.index)
    return res


def do_fft(fid):
    fid_zp = zeropad(fid)
    ft_x, ft_y = fft(fid_zp['fid'], fid.index[1] - fid.index[0])
    return pd.DataFrame(ft_y, index=ft_x, columns=['fft'])


def cut_fid(fid):
    return fid[1400:]


def cut_fft(fft):
    return fft[-350e3:350e3]


def compute_abs_pol(pol, target_irradiation_factor):
    water_fid = process_water_fid(WATER_FID, WATER_DATA_DIR)[1]
    water_pol = compute_water_pol(water_fid)
    pol /= water_pol
    full_pol_ratio = N_RATIO * (1 / target_irradiation_factor) * pol
    abs_pol = WATER_POL * full_pol_ratio * 100
    return abs_pol


def process_water_fid(water_fid, data_dir, weighting=False):
    fid_filepath = os.path.join(data_dir, water_fid['data'])
    fid = load(fid_filepath)
    fid_cutted = fid[1350:]
    if weighting:
        fid['fid'] = weight_signal(fid.index, fid['fid'],
                                   lb=FID_EXP_WEIGHTING)
        fid_cutted['fid'] = weight_signal(fid_cutted.index,
                                          fid_cutted['fid'],
                                          lb=FID_EXP_WEIGHTING)
    electronic_gain_factor = 10 ** (-water_fid['gain'] / 20.)
    fid *= electronic_gain_factor
    fid_cutted *= electronic_gain_factor
    fid *= WATER_SIGNAL_CORRECTION_FACTOR
    fid_cutted *= WATER_SIGNAL_CORRECTION_FACTOR
    return (fid, fid_cutted)


def compute_water_pol(water_fid):
    ft = compute_water_fft(water_fid)
    ft['fft'] = np.real(ft['fft'])
    res = integrate.simps(ft['fft'], ft.index)
    return res


def compute_water_fft(water_fid):
    ft = cut_fft(do_fft(water_fid))
    pc_angle, ft['fft'] = auto_phase_correct(
        ft['fft'], ft.index, step=1.)
    return ft


def compute_pol(data_dir, fids, flip_angle=None, pc=False, weighting=False):
    values = []
    time = []
    for ds in fids:
        fid_filepath = os.path.join(data_dir, ds['data'])
        fid = cut_fid(load(fid_filepath))
        if weighting:
            fid['fid'] = weight_signal(fid.index, fid['fid'],
                                       lb=FID_EXP_WEIGHTING)
        ft = cut_fft(do_fft(fid))
        if pc:
            ft['fft'] = auto_phase_correct(ft['fft'], ft.index,
                                           step=1.)[1]
        ft['fft'] = np.real(ft['fft'])
        res = integrate.simps(ft['fft'], ft.index)
        res *= 10 ** (-ds['gain'] / 20.)
        res *= 1 / np.sin(np.radians(flip_angle))
        values.append(res)
        time.append(ds['t'])
    return pd.DataFrame(values, columns=['P'], index=time)

    
def show_fts(fids, data_dir, data_viewer, prefix='',
             flip_angle=None, auto_pc=False, weighting=False):
    for ds in fids:
        fid_filepath = os.path.join(data_dir, ds['data'])
        fid = load(fid_filepath)
        fid = cut_fid(fid)
        fid *= 10 ** (-ds['gain'] / 20.)
        fid *= 1 / np.sin(np.radians(flip_angle))
        if weighting:
            fid['fid'] = weight_signal(fid.index, fid['fid'],
                                       lb=FID_EXP_WEIGHTING)
        ft = cut_fft(do_fft(fid))
        if auto_pc:
            pc_angle, ft['fft'] = auto_phase_correct(
                ft['fft'], ft.index, step=1.)
        else:
            pc_angle = ds['pc']
            ft['fft'] = phase_correct(ft['fft'], angle=ds['pc'])
        data_viewer.add_object(ft, '{}{} FT (pc={})'
                               .format(prefix, ds['data'], pc_angle))


def show_fids(fids, data_dir, data_viewer, prefix='',
              flip_angle=None, weighting=False):
    for ds in fids:
        fid_filepath = os.path.join(data_dir, ds['data'])
        fid = load(fid_filepath)
        fid_cutted = cut_fid(fid)
        if weighting:
            fid['fid'] = weight_signal(fid.index, fid['fid'],
                                       lb=FID_EXP_WEIGHTING)
            fid_cutted['fid'] = weight_signal(fid_cutted.index,
                                              fid_cutted['fid'],
                                              lb=FID_EXP_WEIGHTING)
        electronic_gain_factor = 10 ** (-ds['gain'] / 20.)
        small_flip_angle_factor = 1 / np.sin(np.radians(flip_angle))
        fid *= electronic_gain_factor
        fid *= small_flip_angle_factor
        fid_cutted *= electronic_gain_factor
        fid_cutted *= small_flip_angle_factor
        data_viewer.add_object(fid, '{}{} FID'
                               .format(prefix, ds['data']))
        data_viewer.add_object(fid_cutted, '{}{} FID (cut)'
                               .format(prefix, ds['data']))


if __name__ == '__main__':
    common.configure_logging()
    dv = data_viewer()

    fid_file = 'ise14.dat'
    fid = load(os.path.join(data2013_dir, fid_file))
    fid['fid'] = weight_signal(fid.index, fid['fid'], lb=FID_EXP_WEIGHTING)
    dv.add_object(fid, 'FID: ' + os.path.basename(fid_file))
    fid_cutted = cut_fid(fid)
    dv.add_object(fid_cutted, 'FID[50:]: ' + os.path.basename(fid_file))
    ft = do_fft(fid_cutted)
    ft_cut = cut_fft(ft)
    dv.add_object(ft_cut, "FFT cut: " + os.path.basename(fid_file))

    theta, ft_phase_corrected = auto_phase_correct(
        ft_cut['fft'], ft_cut.index, step=0.5)
    integr = integrate.simps(np.imag(ft_phase_corrected),
                             ft_cut.index)
    df_pc = pd.DataFrame(ft_phase_corrected, index=ft_cut.index,
                         columns=['fft'])
    dv.add_object(df_pc, 'sample, pc={}, I(Im)={}'
                  .format(theta, integr))

    water_fid, water_fid_cutted = process_water_fid(WATER_FID,
                                                    WATER_DATA_DIR)
    water_ft = compute_water_fft(water_fid_cutted)
    
    dv.add_object(water_fid, '{} FID H2O'
                  .format(WATER_FID['data']))
    dv.add_object(water_fid_cutted, '{} FID H2O (cut)'
                  .format(WATER_FID['data']))
    dv.add_object(water_ft, '{} FT H2O'
                  .format(WATER_FID['data']))
    
    show_fids(buildup2013_fids, data2013_dir, dv,
              flip_angle=small_flip_angle2013, prefix='2013: ')
    show_fids(buildup2014_fids, data2014_dir, dv,
              flip_angle=small_flip_angle2014, prefix='2014: ')
    show_fts(buildup2013_fids, data2013_dir, dv,
             flip_angle=small_flip_angle2013, prefix='2013: ',
             auto_pc=True)
    show_fts(buildup2014_fids, data2014_dir, dv,
             flip_angle=small_flip_angle2014, prefix='2014: ',
             auto_pc=True)
    
    pol_2014 = compute_pol(data2014_dir, buildup2014_fids,
                           flip_angle=small_flip_angle2014, pc=True,
                           weighting=False)
    dv.add_object(pol_2014, 'Pol. 2014 (phase correct)')
    pol_2013 = compute_pol(data2013_dir, buildup2013_fids,
                           flip_angle=small_flip_angle2013, pc=True,
                           weighting=False)
    dv.add_object(pol_2013, 'Pol. 2013 (phase correct)')
    abs_pol_2014 = compute_abs_pol(pol_2014, IRRADIATION_FACTOR_2014)
    dv.add_object(abs_pol_2014, 'Abs. Pol. 2014 (phase correct)')
    abs_pol_2013 = compute_abs_pol(pol_2013, IRRADIATION_FACTOR_2014)
    dv.add_object(abs_pol_2013, 'Abs. Pol. 2013 (phase correct)')

