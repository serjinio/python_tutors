"""
tasks for nmr acquisition
"""


import logging
import os
import tempfile
import subprocess
import shutil

from polpui import config


def acquire(datastore_prefs):
    logging.info('starting NMR acquisition...')
    # _check_exists(config.DO_NMR_EXEC)
    prepare_datastore_path(datastore_prefs.path)
    try:
        tmpdir = tempfile.mkdtemp(prefix='nmr_')
        datafile_path = get_next_datafile_path(datastore_prefs)
        tmp_datafile_path = os.path.join(tmpdir, config.NMR_DATA_FILE_NAME)
        # rc = subprocess.call(config.DO_NMR_EXEC, cwd=tmpdir)
        # to mock real process
        rc = subprocess.call(['touch', '.saveise'], cwd=tmpdir)
        if rc != 0:
            raise RuntimeWarning(('NMR data acquisition subprocess returned '
                                  'non-zero code.'))
        if not os.path.exists(tmp_datafile_path):
            raise RuntimeWarning(('Cannot find NMR data file: "{}"').format(
                tmp_datafile_path))
        shutil.copyfile(tmp_datafile_path, datafile_path)
    finally:
        shutil.rmtree(tmpdir)
    logging.info('NMR acquired in "{}"'.format(datafile_path))
    return datafile_path


def prepare_datastore_path(datastore_path):
    if not os.path.exists(datastore_path):
        make_new_datastore_folder(datastore_path)
    elif os.path.isfile(datastore_path):
        raise ValueError(('Existing file name been specified as a data store '
                          'path: "{}". It should be a directory name.')
                         .format(datastore_path))


def make_new_datastore_folder(datastore_path):
    logging.info('creating new data store directory: "{}"'
                 .format(datastore_path))
    try:
        os.makedirs(datastore_path)
    except Exception as e:
        raise ValueError(('Failed to create new data store directory: '
                          '"{}". Inner exception: {}. Try specifying '
                          'another folder for data storage.')
                         .format(datastore_path, str(e)))


def get_next_datafile_path(datastore_prefs):
    next_data_file_path = datastore_prefs.full_filepath(
        get_last_datafile_number(datastore_prefs) + 1)
    logging.debug('next data file path: "{}"'.format(next_data_file_path))
    return next_data_file_path


def get_last_datafile_number(datastore_prefs):
    logging.debug(('searching for the last recorded data file '
                   'number in folder: "{}"').format(
                       datastore_prefs.path))
    logging.debug('using data storage settings: {}'.format(datastore_prefs))
    flist = [fname for fname in os.listdir(datastore_prefs.path) if
             datastore_prefs.is_filename_matches(fname)]
    fnumbers = [int(datastore_prefs.extract_filename_number_part(fname))
                for fname in flist]
    return max(fnumbers + [0])


def _configure_logging():
    program_path = os.path.dirname(os.path.realpath(__file__))
    logging.config.fileConfig(os.path.join(program_path, 'logging.cfg'))


def _check_exists(exec_path):
    if not os.path.exists(exec_path):
        raise RuntimeWarning('executable does not exists: "{}"'.format(
            exec_path))
