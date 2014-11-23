############################################################
# tasks for NMR acquisition
############################################################


import logging
import os
from invoke import task, run


@task
def sample():
    run("echo hello")


@task
def acquire(datastore_prefs):
    prepare_datastore_path(datastore_prefs.path)
    datafile_path = get_next_datafile_path(datastore_prefs)
    logging.info('starting NMR acquisition...')
    run('touch "{}"'.format(datafile_path))
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
    print flist
    fnumbers = [int(datastore_prefs.extract_filename_number_part(fname))
                for fname in flist]
    return max(fnumbers + [0])


def _configure_logging():
    program_path = os.path.dirname(os.path.realpath(__file__))
    logging.config.fileConfig(os.path.join(program_path, 'logging.cfg'))

