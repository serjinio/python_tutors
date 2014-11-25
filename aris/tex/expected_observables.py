'''
makes plot of expected data values for SAM1URAI13 experiment
'''

import numpy as np
from numpy import sqrt
import matplotlib.pyplot as plt
import pandas as pd


############################################################
# Global config
############################################################

CSV_HEADER_LEN = 5
# plotting

config = {}
exec(open('plot_config.py').read(), config)
print config['plot_params']
plt.rcParams.update(config['plot_params'])


############################################################
# Computation
############################################################


def plot_Ay():
    plt.figure(1)
    plt.clf()

    ay_71 = pd.read_csv('data/Ay_71MeV.csv', sep=',', header=CSV_HEADER_LEN)
    ay_71_sens_down = pd.read_csv('data/Ay_71MeV_sens_down.csv',
                                  sep=',', header=CSV_HEADER_LEN)
    ay_71_sens_up = pd.read_csv('data/Ay_71MeV_sens_up.csv',
                                sep=',', header=CSV_HEADER_LEN)
    
    ay_100 = pd.read_csv('data/Ay_100MeV.csv', sep=',', header=CSV_HEADER_LEN)
    ay_100_sens_down = pd.read_csv('data/Ay_100MeV_sens_down.csv',
                                   sep=',', header=CSV_HEADER_LEN)
    ay_100_sens_up = pd.read_csv('data/Ay_100MeV_sens_up.csv',
                                 sep=',', header=CSV_HEADER_LEN)
    
    ay_200 = pd.read_csv('data/Ay_200MeV.csv', sep=',', header=CSV_HEADER_LEN)
    ay_200_sens_down = pd.read_csv('data/Ay_200MeV_sens_down.csv',
                                   sep=',', header=CSV_HEADER_LEN)
    ay_200_sens_up = pd.read_csv('data/Ay_200MeV_sens_up.csv',
                                 sep=',', header=CSV_HEADER_LEN)
    
    plt.ylim([-2.7, 4.0])
    plt.xlim([0, 2.7])
    plt.locator_params(axis='y', nbins=10)
    plt.locator_params(axis='x', nbins=6)

    plt.fill_between(ay_200_sens_down.q, ay_200_sens_down.Ay,
                     ay_200_sens_up.Ay, facecolor='cyan', lw=0,
                     interpolate=True, alpha=0.5)
    plt.plot(ay_200.q, ay_200.Ay,
             color='red', linewidth=1.0, label='200 MeV/A (-1.5)')
    ay_200_err = ay_200[np.isfinite(ay_200['yerr'])]
    plt.errorbar(ay_200_err.q, ay_200_err.Ay, yerr=ay_200_err.yerr,
                 color='black', fmt='s')

    plt.fill_between(ay_71_sens_down.q, ay_71_sens_down.Ay,
                     ay_71_sens_up.Ay, facecolor='cyan', lw=0,
                     interpolate=True)
    plt.plot(ay_71.q, ay_71.Ay, '--',
             color='red', linewidth=1.0, label='71 MeV/A (+1.5)')
    # plt.plot(ay_71_sens_down.q, ay_71_sens_down.Ay, '--',
    #          color='green', linewidth=1.0)
    # plt.plot(ay_71_sens_up.q, ay_71_sens_up.Ay, '--',
    #          color='green', linewidth=1.0)
    
    plt.axes().fill_between(ay_100_sens_down.q, ay_100_sens_down.Ay,
                            ay_100_sens_up.Ay, facecolor='cyan', lw=0,
                            interpolate=True, alpha=0.5)
    plt.plot(ay_100.q, ay_100.Ay, '-.',
             color='red', linewidth=1.0, label='100 MeV/A')

    xlabel = plt.xlabel('$q\ (fm^{-1})$')
    ylabel = plt.ylabel('$A_y$')
    plt.legend(loc=2)
    plt.savefig('expected_ay.eps', bbox_extra_artists=[xlabel, ylabel],
                bbox_inches='tight')


def plot_cs():
    plt.clf()
    plt.figure(1)
    plt.axes().set_yscale('log')

    cs_71 = pd.read_csv('data/CS_71MeV.csv', sep=',', header=CSV_HEADER_LEN)
    cs_71_sens_down = pd.read_csv('data/CS_71MeV_sens_down.csv',
                                  sep=',', header=CSV_HEADER_LEN)
    cs_71_sens_up = pd.read_csv('data/CS_71MeV_sens_up.csv',
                                sep=',', header=CSV_HEADER_LEN)

    cs_100 = pd.read_csv('data/CS_100MeV.csv', sep=',', header=CSV_HEADER_LEN)
    cs_100_sens_down = pd.read_csv('data/CS_100MeV_sens_down.csv',
                                   sep=',', header=CSV_HEADER_LEN)
    cs_100_sens_up = pd.read_csv('data/CS_100MeV_sens_up.csv',
                                 sep=',', header=CSV_HEADER_LEN)
    
    cs_200 = pd.read_csv('data/CS_200MeV.csv', sep=',', header=CSV_HEADER_LEN)
    cs_200_sens_down = pd.read_csv('data/CS_200MeV_sens_down.csv',
                                   sep=',', header=CSV_HEADER_LEN)
    cs_200_sens_up = pd.read_csv('data/CS_200MeV_sens_up.csv',
                                 sep=',', header=CSV_HEADER_LEN)

    plt.xlim([0, 2.7])
    plt.locator_params(axis='x', nbins=6)

    plt.fill_between(cs_71_sens_down.q, cs_71_sens_down.CS,
                     cs_71_sens_up.CS, facecolor='cyan', lw=0,
                     interpolate=True, alpha=0.5)
    plt.plot(cs_71.q, cs_71.CS, '--',
             color='red', linewidth=1.0, label='71 MeV/A')

    plt.axes().fill_between(cs_100_sens_down.q, cs_100_sens_down.CS,
                            cs_100_sens_up.CS, facecolor='cyan', lw=0,
                            interpolate=True, alpha=0.5)
    plt.plot(cs_100.q, cs_100.CS, '-.',
             color='red', linewidth=1.0, label='100 MeV/A')

    plt.axes().fill_between(cs_200_sens_down.q, cs_200_sens_down.CS,
                            cs_200_sens_up.CS, facecolor='cyan', lw=0,
                            interpolate=True, alpha=0.5)
    plt.plot(cs_200.q, cs_200.CS,
             color='red', linewidth=1.0, label='200 MeV/A')
    cs_200_err = cs_200[np.isfinite(cs_200['yerr'])]
    plt.errorbar(cs_200_err.q, cs_200_err.CS, yerr=cs_200_err.yerr,
                 color='black', fmt='s')

    xlabel = plt.xlabel('$q\ (fm^{-1})$')
    ylabel = plt.ylabel('${d \\sigma} / {d \\Omega}\ (mb/sr)$')
    plt.legend(loc=1)
    plt.savefig('expected_cs.eps', bbox_extra_artists=[xlabel, ylabel],
                bbox_inches='tight')


if __name__ == '__main__':
    plot_Ay()
    plot_cs()
