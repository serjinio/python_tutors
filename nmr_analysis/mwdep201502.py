

import os

import numpy as np
import pandas as pd
from scipy import integrate

from nmran.analyse import fft, zeropad, auto_phase_correct, \
    phase_correct, weight_signal, _compute_exp_window
from nmran.dataio import load
from nmran.datavis import data_viewer
from nmran import common


FID_EXP_WEIGHTING = 5.


data2014_dir = '/Users/serj/projects/polp_data/1220/'
mwdep2014_fids = [
    {'data': 'ise50.dat', 'gain': 80, 'pc': 90, 'P': 0},
    {'data': 'ise48.dat', 'gain': 80, 'pc': 300, 'P': 0.4},
    {'data': 'ise57.dat', 'gain': 80, 'pc': 300, 'P': 0.65},
    {'data': 'ise60.dat', 'gain': 80, 'pc': 300, 'P': 1},
    {'data': 'ise62.dat', 'gain': 80, 'pc': 300, 'P': 1.6},
    {'data': 'ise72.dat', 'gain': 80, 'pc': 315, 'P': 2.5},
    {'data': 'ise64.dat', 'gain': 80, 'pc': 330, 'P': 3.5},
    {'data': 'ise68.dat', 'gain': 80, 'pc': 330, 'P': 5.0},
    {'data': 'ise66.dat', 'gain': 80, 'pc': 330, 'P': 6.5},
    {'data': 'ise70.dat', 'gain': 80, 'pc': 330, 'P': 8.0},
    {'data': 'ise43.dat', 'gain': 80, 'pc': 315, 'P': 11.6},
    {'data': 'ise76.dat', 'gain': 80, 'pc': 330, 'P': 14}
]

data2015_dir = '/Users/serj/projects/polp_data/02xx/'
mwdep2015_fids = [
    {'data': 'ise50.dat', 'gain': 80, 'P': 0},
]


def do_fft(fid):
    fid_zp = zeropad(fid)
    ft_x, ft_y = fft(fid_zp['fid'], fid.index[1] - fid.index[0])
    return pd.DataFrame(ft_y, index=ft_x, columns=['fft'])


def cut_fid(fid):
    return fid[1400:]


def cut_fft(fft):
    return fft[-350e3:350e3]


def compute_mwdep(fids, data_dir, pc=False, weighting=False):
    values = []
    arguments = []
    res = 0.
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
            res = integrate.simps(np.real(ft['fft']), ft.index)
        else:
            res = integrate.simps(np.abs(ft['fft']), ft.index)
        res *= 10 ** (-ds['gain'] / 20.)
        values.append(res)
        arguments.append(np.sqrt(ds['P']))
    return pd.DataFrame(values, columns=['Pol'], index=arguments)


def show_fts(fids, data_dir, data_viewer,
             pc=False, prefix='', weighting=False):
    for ds in fids:
        fid_filepath = os.path.join(data_dir, ds['data'])
        fid = cut_fid(load(fid_filepath))
        if weighting:
            fid['fid'] = weight_signal(fid.index, fid['fid'],
                                       lb=FID_EXP_WEIGHTING)
        electronic_gain_factor = 10 ** (-ds['gain'] / 20.)
        fid *= electronic_gain_factor
        ft = cut_fft(do_fft(fid))
        if pc:
            ft['fft'] = auto_phase_correct(ft['fft'], ft.index,
                                           step=1.)[1]
        data_viewer.add_object(ft, '{}{} FT'.format(prefix, ds['data']))


def show_fids(fids, data_dir, data_viewer, prefix='',
              weighting=False):
    for ds in fids:
        fid_filepath = os.path.join(data_dir, ds['data'])
        fid = load(fid_filepath)
        fid_cutted = cut_fid(fid)
        if weighting:
            fid_cutted['fid'] = weight_signal(
                fid_cutted.index, fid_cutted['fid'], lb=FID_EXP_WEIGHTING)
        electronic_gain_factor = 10 ** (-ds['gain'] / 20.)
        fid *= electronic_gain_factor
        fid_cutted *= electronic_gain_factor
        data_viewer.add_object(fid, '{}{} FID'
                               .format(prefix, ds['data']))
        data_viewer.add_object(fid_cutted, '{}{} FID (cut)'
                               .format(prefix, ds['data']))

    
if __name__ == '__main__':
    common.configure_logging()
    dv = data_viewer()
    
    show_fids(mwdep2014_fids, data2014_dir, dv,
              prefix='2014: ', weighting=True)
    show_fts(mwdep2014_fids, data2014_dir, dv,
             pc=True, weighting=True, prefix='2014: ')
    
    mwdep2014 = compute_mwdep(mwdep2014_fids, data2014_dir,
                              pc=True, weighting=True)
    dv.add_object(mwdep2014, 'MW dep 2014')
