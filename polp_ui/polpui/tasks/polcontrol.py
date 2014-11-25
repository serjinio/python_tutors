"""
tasks for control of hardware for polarization
"""


import logging
import os
import subprocess

from polpui import config


def mw_on():
    logging.info('turning on MW')
    _check_exists(config.MW_ON_EXEC)
    rc = subprocess.call(config.MW_ON_EXEC)
    if rc != 0:
        raise RuntimeWarning(
            ('MW turn on subprocess: "{}" returned non-zero '
             'return code: {}').format(config.MW_ON_EXEC, rc))
    logging.info('WM turned on')


def mw_off():
    logging.info('turning off MW')
    _check_exists(config.MW_OFF_EXEC)
    rc = subprocess.call(config.MW_OFF_EXEC)
    if rc != 0:
        raise RuntimeWarning(
            ('MW turn off subprocess: "{}" returned non-zero '
             'return code: {}').format(config.MW_OFF_EXEC, rc))
    logging.info('MW turned off')


def _check_exists(exec_path):
    if not os.path.exists(exec_path):
        raise RuntimeWarning('executable does not exists: "{}"'.format(
            exec_path))
