

import os

import numpy as np
import pandas as pd

from nmran.analyse import fft, integrate_fft, zeropad
from nmran.dataio import load
from nmran.datavis import data_viewer
from nmran import common


data_dir = '/home/serj/Desktop/0925/'
mwdep_fids = [
    'ise25.dat',
    'ise15.dat'
]


def process_fid(fid):
    ft = cut_fft(do_fft(cut_fid(fid)))
    res = integrate_fft(ft)
    return res


def do_fft(fid):
    fid_zp = zeropad(fid)
    fid_fft = fft(fid_zp)
    return fid_fft


def cut_fid(fid):
    return fid[50:]


def cut_fft(fft):
    return fft[-350e3:350e3]


def compute_mwdep():
    values = []
    for idx, fid_file in enumerate(mwdep_fids):
        fid_filepath = os.path.join(data_dir, fid_file)
        fid = load(fid_filepath)
        res = process_fid(fid)
        values.append(res)
    return pd.DataFrame(values, columns=['I'])


if __name__ == '__main__':
    common.configure_logging()
    dv = data_viewer()

    fid_file = 'ise25.dat'
    fid = load(os.path.join(data_dir, 'ise25.dat'))
    dv.add_object(fid, 'FID: ' + os.path.basename(fid_file))

    fid_cutted = cut_fid(fid)
    dv.add_object(fid_cutted, 'FID[50:]: ' + os.path.basename(fid_file))

    ft = do_fft(fid_cutted)
    dv.add_object(ft, "FFT: " + os.path.basename(fid_file))
    ft_cut = cut_fft(ft)
    dv.add_object(ft_cut, "FFT cut: " + os.path.basename(fid_file))

    mwdep = compute_mwdep()
    dv.add_object(mwdep, 'FID int: ' + os.path.basename(fid_file))
