"""
tasks for control of hardware for polarization
"""


import logging

from polpui import config
from polpui.tasks.common import execute


def mw_on():
    logging.info('turning on MW')
    execute(config.MW_ON_EXEC)
    logging.info('WM turned on')


def mw_off():
    logging.info('turning off MW')
    execute(config.MW_OFF_EXEC)
    logging.info('MW turned off')
