############################################################
# UI front-end for polp:
#  - acquisition of NMR signals
#  - MW system control: turn on  polarization cycle
#
# all hardware functions are handled by respective utilities
# written separately from this module. This module only
# contains UI elements for user interaction
############################################################


import os
import datetime
from Tkinter import *
import ttk
import logging
import logging.config

import config
from polpcommon import DataStorePrefs
from polptasks import nmr


class PolpUi(object):
    '''
    Main application window.
    '''

    def __init__(self, tk_root):
        self._tk_root = tk_root
        self._init_ui()

    def show(self):
        self._tk_root.mainloop()

    def _init_ui(self):
        self._tk_root.title('Polp')
        self._setup_layout()
        self._init_frames()
        self._init_nmr_control_ui()
        self._init_polp_cycle_control_ui()

    def _setup_layout(self):
        self._tk_root.columnconfigure(0, weight=75)
        self._tk_root.resizable(height=FALSE)

    def _init_frames(self):
        self._nmr_frame = ttk.Frame(self._tk_root, padding="12 12 12")
        self._nmr_frame.grid(column=0, row=0, sticky=(N, W, E, S))
        self._pol_frame = ttk.Frame(self._tk_root, padding="12 12 12 12")
        self._pol_frame.grid(column=1, row=0, sticky=(N, W, E, S))

    def _init_nmr_control_ui(self):
        self._nmr_control_ui = NmrControlUi(
            self._nmr_frame,
            DataStorePrefs(self._get_nmr_data_dir(),
                           config.NMR_FILENAME_PREFIX,
                           config.NMR_FILENAME_SUFFIX))

    def _init_polp_cycle_control_ui(self):
        self._polp_cycle_control_ui = PolpCycleControlUi(self._pol_frame)

    def _get_nmr_data_dir(self):
        data_dir = config.NMR_DATA_DIR
        if config.NMR_DATA_DIR_APPEND_DATE_SUFFIX:
            data_dir = os.path.join(
                data_dir, datetime.datetime.now().strftime('%d%m'))
        return data_dir


class NmrControlUi(object):

    def __init__(self, parent, datastore_prefs):
        self._parent = parent

        self._data_folder = StringVar()
        self._data_folder.set(datastore_prefs.path)
        self._data_file_name_prefix = StringVar()
        self._data_file_name_prefix.set(datastore_prefs.filename_prefix)
        self._data_file_name_suffix = StringVar()
        self._data_file_name_suffix.set(datastore_prefs.filename_suffix)
        self._last_data_file = StringVar()

        self._init_ui()

    def _init_ui(self):
        self._parent.columnconfigure(1, weight=40)
        self._parent.columnconfigure(3, weight=40)

        ttk.Label(self._parent, text='Data folder:').grid(
            column=0, row=0, sticky=E)
        self._data_folder_entry = ttk.Entry(
            self._parent, textvariable=self._data_folder, width=40)
        self._data_folder_entry.grid(
            column=1, row=0, columnspan=4, padx=5, sticky=(E, W))

        ttk.Label(self._parent, text='File name format:').grid(
            column=0, row=1, pady=5, sticky=E)
        self._data_file_name_prefix_entry = ttk.Entry(
            self._parent, textvariable=self._data_file_name_prefix).grid(
                column=1, row=1, padx=5, sticky=(E, W))
        ttk.Label(self._parent, text='###').grid(
            column=2, row=1, padx=5, sticky=(E, W))
        self._data_file_name_suffix_entry = ttk.Entry(
            self._parent, textvariable=self._data_file_name_suffix).grid(
                column=3, row=1, columnspan=2, padx=5, sticky=(E, W))

        ttk.Label(self._parent, text='Last data file:').grid(
            column=0, row=2, pady=5, sticky=E)
        self._last_data_file_entry = ttk.Entry(
            self._parent, textvariable=self._last_data_file)
        self._last_data_file_entry.grid(
            column=1, row=2, columnspan=4, padx=5, sticky=(E, W))
        self._last_data_file_entry.configure(state='readonly')

        self._nmr_button = ttk.Button(
            self._parent, text="NMR", command=self._take_nmr)
        self._nmr_button.grid(
            column=3, row=3, sticky=E, pady=10)
        self._view_nmr_button = ttk.Button(
            self._parent, text="View")
        self._view_nmr_button.grid(
            column=4, row=3, sticky=E, pady=10, padx=5)

    def _take_nmr(self, *args):
        data_file = nmr.acquire(DataStorePrefs(
            self._data_folder.get(), self._data_file_name_prefix.get(),
            self._data_file_name_suffix.get()))
        self._last_data_file.set(data_file)


class PolpCycleControlUi(object):

    def __init__(self, parent):
        self._parent = parent
        self._mode = StringVar()
        self._init_ui()

    def _init_ui(self):
        ttk.Label(self._parent, text='Polarization control:').grid(
            column=0, row=0, columnspan=2, sticky=W)
        ttk.Radiobutton(self._parent, text='Polarization mode',
                        variable=self._mode, value='pol').grid(
                            column=0, row=1, sticky=W, padx=10, pady=5)
        ttk.Radiobutton(self._parent, text='NMR mode',
                        variable=self._mode, value='nmr').grid(
                            column=0, row=2, sticky=W, padx=10, pady=5)


def _configure_logging():
    program_path = os.path.dirname(os.path.realpath(__file__))
    logging.config.fileConfig(os.path.join(program_path, 'logging.cfg'))


if __name__ == '__main__':
    _configure_logging()

    logging.info('launching polp ui')
    tk_root = Tk()
    polp_ui = PolpUi(tk_root)
    polp_ui.show()
