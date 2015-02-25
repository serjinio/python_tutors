

import os

import numpy as np
import pandas as pd
from scipy import integrate

from nmran.analyse import fft, zeropad, auto_phase_correct, \
    phase_correct, weight_signal, _compute_exp_window
from nmran.dataio import load
from nmran.datavis import data_viewer
from nmran import common


FID_EXP_WEIGHTING = 3.


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

random_data_dir = '/Users/serj/projects/polp_data/2015/0225/'
random_fids = [
    {'data': 'ise3.dat', 'gain': 100, 'P': 3.5},
    {'data': 'ise11.dat', 'gain': 80, 'P': 3.5},
    {'data': 'ise12.dat', 'gain': 80, 'P': 3.5},
    {'data': 'ise13.dat', 'gain': 80, 'P': 3.5},
    {'data': 'ise14.dat', 'gain': 80, 'P': 6.0},
]

reprod_data_dir = '/Users/serj/projects/polp_data/2015/0225/'
reprod_fids = [
    {'data': 'ise13.dat', 'gain': 80},
    {'data': 'ise17.dat', 'gain': 80},
    {'data': 'ise20.dat', 'gain': 80},
    {'data': 'ise22.dat', 'gain': 80},
    {'data': 'ise33.dat', 'gain': 80},
    {'data': 'ise36.dat', 'gain': 80},
    {'data': 'ise39.dat', 'gain': 80},
    {'data': 'ise43.dat', 'gain': 80},
    {'data': 'ise49.dat', 'gain': 80},
    {'data': 'ise51.dat', 'gain': 80},
    {'data': 'ise53.dat', 'gain': 80},
    {'data': 'ise58.dat', 'gain': 80},
    {'data': 'ise64.dat', 'gain': 80},
]

# orange & fiber laser efficiency
# comparing two 1 min build-upswith highest rep. rate for each laser
lasers_eff_dir = "/Users/serj/projects/polp_data/2015/0225/lasers_eff"
lasers_eff_fids = [
    {'data': 'orange_1min.dat', 'gain': 80, 'P': 5.0},
    {'data': 'fiber_1min.dat', 'gain': 80, 'P': 5.0},
]

crystal_angle_dir = "/Users/serj/projects/polp_data/2015/0225/"
crystal_angle_fids = [
    {'data': 'ise80.dat', 'gain': 80, 'angle': -30.0},
    {'data': 'ise77.dat', 'gain': 80, 'angle': -15.0},
    {'data': 'ise82.dat', 'gain': 80, 'angle': -1.0},
    {'data': 'ise69.dat', 'gain': 80, 'angle': +1.0},
    {'data': 'ise72.dat', 'gain': 80, 'angle': 15.0},
    {'data': 'ise75.dat', 'gain': 80, 'angle': 30.0},
]


def do_fft(fid):
    fid_zp = zeropad(fid)
    ft_x, ft_y = fft(fid_zp['fid'], fid.index[1] - fid.index[0])
    return pd.DataFrame(ft_y, index=ft_x, columns=['fft'])


def cut_fid(fid):
    return fid[1500:]
    # return fid[1900:]


def cut_fft(fft):
    return fft[-120e3:120e3]

    
def compute(fids, data_dir, pc=False, weighting=False, arg='index'):
    values = []
    arguments = []
    res = 0.
    idx = 0
    for ds in fids:
        fid_filepath = os.path.join(data_dir, ds['data'])
        fid = cut_fid(load(fid_filepath))
        if weighting:
            fid['fid'] = weight_signal(fid.index, fid['fid'],
                                       lb=FID_EXP_WEIGHTING)
        ft = cut_fft(do_fft(fid))
        if pc:
            ft['fft'] = auto_phase_correct(ft['fft'], ft.index,
                                           step=3.)[1]
            res = integrate.simps(np.real(ft['fft']), ft.index)
        else:
            res = integrate.simps(np.abs(ft['fft']), ft.index)
        res *= 10 ** (-ds['gain'] / 20.)
        values.append(res)
        if arg == 'index':
            arguments.append(idx)
            idx += 1
        else:
            arguments.append(ds[arg])
    return pd.DataFrame(values, columns=['Pol'], index=arguments)


def compute_mwdep(fids, data_dir, pc=False, weighting=False):
    return compute(fids, data_dir, pc=pc, weighting=weighting, arg='P')


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


def show_dataset(fids, data_dir, title="New Dataset", prefix='', arg="index"):
    dep = compute(fids, data_dir,
                  pc=True, weighting=True, arg=arg)
    show_fids(fids, data_dir, dv,
              prefix=prefix, weighting=True)
    show_fts(fids, data_dir, dv,
             pc=True, weighting=True, prefix=prefix)
    dv.add_object(dep, title)

    
if __name__ == '__main__':
    # globals
    common.configure_logging()
    dv = data_viewer()
    
    show_dataset(mwdep2014_fids, data2014_dir, title='MW Dep. (12/2014)',
                 prefix='2014: ', arg='P')

    show_dataset(random_fids, random_data_dir,
                 'Random FIDs')

    show_dataset(reprod_fids, reprod_data_dir,
                 'Reprod. (3 points for a set)', prefix='Reprod. ')
    
    show_dataset(lasers_eff_fids, lasers_eff_dir,
                 'Orange & fiber lasers', 'Lasers: ')
    
    show_dataset(crystal_angle_fids, crystal_angle_dir,
                 title='Crystal Angle', prefix='Cryst. Ang.: ', arg='angle')


