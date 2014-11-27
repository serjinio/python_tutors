############################################################
# Module with common routines for polp app
############################################################


import os
import os.path
import numbers
import csv
import logging
import logging.config


def list_files_matching_prefs(datastore_prefs):
    '''Function returns list of files matching to a provided
    DataStorePrefs object.
    '''
    if not os.path.isdir(datastore_prefs.path):
        return []
    matching = []
    for f in os.listdir(datastore_prefs.path):
        if datastore_prefs.is_filename_matches(f):
            matching.append(f)
    return matching


def list_files_matching_extension(path, extensions_list):
    '''Function returns list of files from provided folder which extension
    matches to a given extensions_list.
    '''
    if not os.path.isdir(path):
        return []
    matching = []
    for f in os.listdir(path):
        if os.path.isfile(os.path.join(path, f)) and \
           any([f.endswith(ext) for ext in extensions_list]):
            matching.append((f, os.stat(os.path.join(path, f)).st_ctime))
    if len(matching) > 0:
        matching.sort(key=lambda el: el[1])
        matching = zip(*matching)[0]
    return matching


KNOWN_DATA_FILE_FORMATS = ['.smd', '.dat']


def load_data_file(filepath):
    '''Loads data from a file of known format.'''
    if not any(filepath.endswith(fmt) for fmt in KNOWN_DATA_FILE_FORMATS):
        raise ValueError(('Input file seems to be of unknown format. '
                          'supported formats are: {}'.format(
                              KNOWN_DATA_FILE_FORMATS)))
    if filepath.endswith(KNOWN_DATA_FILE_FORMATS[0]):
        return _load_smd(filepath)
    elif filepath.endswith(KNOWN_DATA_FILE_FORMATS[1]):
        return _load_dat(filepath)


def _load_smd(filepath):
    logging.debug('reading data file: "{}"'.format(filepath))
    if not os.path.exists(filepath):
        raise ValueError('Given file path: "{}" does not exists.'
                         .format(filepath))
    x_data, y_data = [], []
    errors_count = 0
    with open(filepath, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', skipinitialspace=True)
        for row in reader:
            if errors_count > 20:
                raise ValueError(('File provided: "{}" does not seem to be '
                                  'a valid .dat file, load aborted.')
                                 .format(filepath))
            # only rows with 2 columns are a valid data rows
            if len(row) == 2:
                y_data.append(complex(float(row[0]), float(row[1])))
            else:
                errors_count += 1
    # header params
    with file(filepath, 'rb') as input_file:
        npoints, dwell, sf1 = [input_file.readline() for i in range(0, 3)]
    npoints, dwell, sf1 = int(npoints[6:]), float(dwell[3:]), float(sf1[4:])
    logging.debug('header data: npoints={}; dwell={}, sf1={}'
                  .format(npoints, dwell, sf1))
    x_data = [dwell * n for n in range(len(y_data))]
    ds = DataSet(x_data, y_data, os.path.basename(filepath),
                 'Time [us]', 'Amplitude [V]')
    logging.debug('read dataset: \n{}'.format(ds))
    return ds


def _load_dat(filepath):
    logging.debug('reading data file: "{}"'.format(filepath))
    if not os.path.exists(filepath):
        raise ValueError('Given file path: "{}" does not exists.'
                         .format(filepath))
    x_data, y_data = [], []
    errors_count = 0
    with open(filepath, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', skipinitialspace=True)
        for row in reader:
            if errors_count > 20:
                raise ValueError(('File provided: "{}" does not seem to be '
                                  'a valid .dat file, load aborted.')
                                 .format(filepath))
            if len(row) >= 3:
                try:
                    x_data.append(float(row[0]) * 1e6)
                    y_data.append(complex(float(row[1]), float(row[2])))
                except:
                    logging.warn('failed to load data row: {}'.format(row))
                    errors_count += 1
            else:
                errors_count += 1
    logging.debug('error count in data file: {}'.format(errors_count))
    dataset = DataSet(x_data, y_data, os.path.basename(filepath),
                      'Time [us]', 'Amplitude [V]')
    logging.debug('read data: \n{}'.format(dataset))
    return dataset


def reduce_dataset(dataset):
    """Reduces dataset size to at max 1500 points to make it
    faster to plot. This might discard some sharp peaks in the plot."""
    draw_stride = 1. if len(dataset) < 750 else \
        int(len(dataset) / 750.)
    x_data = [x for idx, x in enumerate(dataset.x_data)
              if idx % draw_stride == 0]
    y_data = [y for idx, y in enumerate(dataset.y_data)
              if idx % draw_stride == 0]
    return DataSet(x_data, y_data, dataset.title,
                   dataset.x_data_name, dataset.y_data_name)


class DataStorePrefs(object):
    '''Object holds settings for data storage.'''

    def __init__(self, datastore_path, filename_prefix, filename_suffix):
        self._store_path = datastore_path
        self._filename_prefix = filename_prefix
        self._filename_suffix = filename_suffix

    @property
    def path(self):
        return self._store_path

    @property
    def filename_prefix(self):
        return self._filename_prefix

    @property
    def filename_suffix(self):
        return self._filename_suffix

    def filename(self, file_number):
        '''Returns full file name based on provided number argument.'''
        if not str(file_number).isdigit():
            raise ValueError('Provided argument: "{}" is not a number.'.format(
                file_number))
        return self._filename_prefix + str(file_number) + self._filename_suffix

    def full_filepath(self, file_number):
        return os.path.join(self._store_path, self.filename(file_number))

    def is_filename_matches(self, filename):
        if filename.startswith(self.filename_prefix) and \
           filename.endswith(self.filename_suffix):
            number_part = self.extract_filename_number_part(filename)
            if number_part.isdigit():
                return True

        return False

    def extract_filename_number_part(self, filename):
        return filename[len(self.filename_prefix):
                        len(filename) - len(self.filename_suffix)]

    def __str__(self):
        return 'Store path: "{}". Prefix & suffix: "{}" & "{}"'.format(
            self.path, self.filename_prefix, self.filename_suffix)


class DataSet(object):

    def __init__(self, x_data, y_data, title='',
                 x_data_name='Argument', y_data_name='Value'):
        self._x_data = x_data
        self._y_data = y_data
        self.title = title
        self.x_data_name = x_data_name
        self.y_data_name = y_data_name
        self._validate()

    @property
    def x_data(self):
        if len(self._x_data) > 0:
            return self._x_data
        else:
            return [0., 0.]

    @property
    def y_data(self):
        if len(self._y_data) > 0:
            return self._y_data
        else:
            return [0., 0.]
    
    def is_y_data_complex(self):
        if len(self.y_data) == 0:
            return False
        return isinstance(self.y_data[0], complex)

    def abs_y_data(self):
        '''Returns absolute values in case y data of this dataset is
        complex-valued.'''
        if self.is_y_data_complex():
            return [abs(y) for y in self.y_data]
        else:
            return self.y_data

    def _validate(self):
        if len(self.x_data) != len(self.y_data):
            raise ValueError(('Lengths of input data for X and Y values are '
                              'different: {} and {}. Invalid input data!')
                             .format(len(self.x_data), len(self.y_data)))
        # will check 10 first values, that it is correct numeric data
        upper_limit = 10 if len(self.y_data) > 10 else len(self.y_data)
        if any([not isinstance(x, numbers.Number)
                for x in self.x_data[:upper_limit]]):
            raise ValueError(('Some of x values provided are not number(s)!'
                              'it is invalid data!'))
        if any([not isinstance(y, numbers.Number)
                for y in self.y_data[:upper_limit]]):
            raise ValueError(('Some of y values provided are not number(s)!'
                              'it is invalid data!'))

    def xlimits(self):
        """Return min & max X coordinates on this dataset."""
        if len(self) > 0:
            min_x = min(self.x_data)
            max_x = max(self.x_data)
            return (min_x, max_x)
        else:
            return (0., 0.)

    def ylimits(self):
        """Return min & max Y coordinates on this dataset."""
        if len(self) > 0:
            min_y = min(self.y_data)
            max_y = max(self.y_data)
            return (min_y, max_y)
        else:
            return (0., 0.)

    def __str__(self):
        res = 'Dataset: "{}" ({} points):'.format(self.title, len(self.x_data))
        upper_limit = 7 if len(self.x_data) > 10 else len(self.x_data)
        for i in range(0, upper_limit):
            res += '\n {}; {}'.format(self.x_data[i], self.y_data[i])
        res += '\n ...'
        return res

    def __len__(self):
        return len(self.x_data)


INVALID_DATA_SET = DataSet([0., 0.], [0., 0.], 'Bad dataset')


def _configure_logging():
    program_path = os.path.dirname(os.path.realpath(__file__))
    logging.config.fileConfig(os.path.join(program_path, 'logging.cfg'))


if __name__ == '__main__':
    _configure_logging()
