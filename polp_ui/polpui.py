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
    """Class for main application window."""

    def __init__(self, tk_root):
        self._tkRoot = tk_root
        self._init_ui()

    def show(self):
        self._tkRoot.mainloop()

    def _init_ui(self):
        self._tkRoot.title('Polp')
        self._setup_layout()
        self._init_frames()
        self._init_nmr_control_ui()
        self._init_polp_control_ui()

    def _setup_layout(self):
        self._tkRoot.columnconfigure(0, weight=75)
        self._tkRoot.resizable(height=FALSE, width=FALSE)

    def _init_frames(self):
        self._frmNmr = ttk.Frame(self._tkRoot, padding="12 12 12")
        self._frmPol = ttk.Frame(self._tkRoot, padding="12 12 12 12")
        self._frmNmr.grid(column=0, row=0, sticky=(N, W, E, S))
        self._frmPol.grid(column=1, row=0, sticky=(N, W, E, S))

    def _init_nmr_control_ui(self):
        self._uiNmrControl = NmrControlUi(
            self._frmNmr,
            DataStorePrefs(self._get_nmr_data_dir(),
                           config.NMR_FILENAME_PREFIX,
                           config.NMR_FILENAME_SUFFIX))

    def _init_polp_control_ui(self):
        self._uiPolpControl = PolpCycleControlUi(self._frmPol)

    def _get_nmr_data_dir(self):
        data_dir = config.NMR_DATA_DIR
        if config.NMR_DATA_DIR_APPEND_DATE_SUFFIX:
            data_dir = os.path.join(
                data_dir, datetime.datetime.now().strftime('%d%m'))
        return data_dir


class NmrControlUi(object):

    def __init__(self, parent, datastore_prefs):
        self._parent = parent
        self._varDataFolder = StringVar(value=datastore_prefs.path)
        self._varDataFileNamePrefix = StringVar(
            value=datastore_prefs.filename_prefix)
        self._varDataFileNameSuffix = StringVar(
            value=datastore_prefs.filename_suffix)
        self._varDataFile = StringVar()
        self._init_ui()

    def _init_ui(self):
        self._parent.columnconfigure(1, weight=40)
        self._parent.columnconfigure(3, weight=40)

        ttk.Label(self._parent, text='Data folder:').grid(
            column=0, row=0, sticky=E)
        self._entDataFolder = ttk.Entry(
            self._parent, textvariable=self._varDataFolder, width=40)
        self._entDataFolder.grid(
            column=1, row=0, columnspan=4, padx=5, sticky=(E, W))

        ttk.Label(self._parent, text='File name format:').grid(
            column=0, row=1, pady=5, sticky=E)
        self._entDataFileNamePrefix = ttk.Entry(
            self._parent, textvariable=self._varDataFileNamePrefix).grid(
                column=1, row=1, padx=5, sticky=(E, W))
        ttk.Label(self._parent, text='###').grid(
            column=2, row=1, padx=5, sticky=(E, W))
        self._entDataFileNameSuffix = ttk.Entry(
            self._parent, textvariable=self._varDataFileNameSuffix).grid(
                column=3, row=1, columnspan=2, padx=5, sticky=(E, W))

        ttk.Label(self._parent, text='Last data file:').grid(
            column=0, row=2, pady=5, sticky=E)
        self._entDataFile = ttk.Entry(
            self._parent, textvariable=self._varDataFile)
        self._entDataFile.grid(
            column=1, row=2, columnspan=4, padx=5, sticky=(E, W))
        self._entDataFile.configure(state='readonly')

        self._btnNmr = ttk.Button(self._parent, text="NMR",
                                  command=self._take_nmr)
        self._btnNmr.grid(column=3, row=3, sticky=E, pady=10)
        self._btnView = ttk.Button(self._parent, text="View",
                                   command=self._view_data)
        self._btnView.grid(column=4, row=3, sticky=E, pady=10, padx=5)

    def _take_nmr(self, *args):
        data_file = nmr.acquire(DataStorePrefs(
            self._varDataFolder.get(), self._varDataFileNamePrefix.get(),
            self._varDataFileNameSuffix.get()))
        self._varDataFile.set(data_file)

    def _view_data(self):
        from dataviewer import data_viewer
        data_viewer(self._varDataFolder.get())


class PolpCycleControlUi(object):

    def __init__(self, parent):
        self._parent = parent
        self._varMode = StringVar()
        self._init_ui()

    def _init_ui(self):
        ttk.Label(self._parent, text='Polarization control:').grid(
            column=0, row=0, columnspan=2, sticky=W)
        ttk.Radiobutton(self._parent, text='Polarization mode',
                        variable=self._varMode, value='pol').grid(
                            column=0, row=1, sticky=W, padx=10, pady=5)
        ttk.Radiobutton(self._parent, text='NMR mode',
                        variable=self._varMode, value='nmr').grid(
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
