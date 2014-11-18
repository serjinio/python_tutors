############################################################
# Module with common routines for polp app
############################################################


import os


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
