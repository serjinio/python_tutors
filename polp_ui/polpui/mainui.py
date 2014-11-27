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
import tkFileDialog
import ttk
import logging
import logging.config

import config
from common import DataStorePrefs
from tasks import nmr
from tasks import polcontrol


def start_app():
    _configure_logging()
    logging.info('launching polp ui')
    tk_root = Tk()
    polp_ui = PolpUi(tk_root)
    polp_ui.show()


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
        self._dataviewer = None
        self._init_ui()

    def _init_ui(self):
        self._parent.columnconfigure(1, weight=40)
        self._parent.columnconfigure(3, weight=40)

        self._lblDataFolder = ttk.Label(self._parent, text='Data folder:')
        self._btnChangeDir = ttk.Button(
            self._parent, text="CD", command=self._select_dir)
        self._entDataFolder = ttk.Entry(
            self._parent, textvariable=self._varDataFolder)
        
        self._lblFileNameFormat = ttk.Label(self._parent,
                                            text='File name format:')
        self._entDataFileNamePrefix = ttk.Entry(
            self._parent, textvariable=self._varDataFileNamePrefix)
        self._lblDataFileNumber = ttk.Label(self._parent, text='###')
        self._entDataFileNameSuffix = ttk.Entry(
            self._parent, textvariable=self._varDataFileNameSuffix)
        self._lblLastDataFile = ttk.Label(self._parent,
                                          text='Last data file:')
        self._entDataFile = ttk.Entry(
            self._parent, textvariable=self._varDataFile)
        
        self._btnNmr = ttk.Button(self._parent, text="NMR",
                                  command=self._take_nmr)
        self._btnView = ttk.Button(self._parent, text="View",
                                   command=self._view_data)
                
        self._lblDataFolder.grid(column=0, row=0, sticky=E)
        self._lblFileNameFormat.grid(
            column=0, row=1, pady=5, sticky=E)
        self._entDataFileNamePrefix.grid(
            column=1, row=1, padx=5, sticky=(E, W))
        self._lblDataFileNumber.grid(
            column=2, row=1, padx=5, sticky=(E, W))
        self._entDataFileNameSuffix.grid(
            column=3, row=1, columnspan=3, padx=5, sticky=(E, W))
        self._entDataFile.grid(
            column=1, row=2, columnspan=5, padx=5, sticky=(E, W))
        self._entDataFile.configure(state='readonly')
        self._entDataFolder.grid(
            column=1, row=0, columnspan=4, padx=5, sticky=(E, W))
        self._btnChangeDir.grid(
            column=5, row=0, padx=0)
        self._btnChangeDir.config(width=3)
        self._lblLastDataFile.grid(
            column=0, row=2, pady=5, sticky=E)
        self._btnNmr.grid(column=3, row=3, sticky=E, pady=10)
        self._btnView.grid(column=4, columnspan=2, row=3, sticky=E,
                           pady=10, padx=5)

    def _take_nmr(self, *args):
        data_file = nmr.acquire(DataStorePrefs(
            self._varDataFolder.get(), self._varDataFileNamePrefix.get(),
            self._varDataFileNameSuffix.get()))
        self._varDataFile.set(data_file)
        if self._is_dataviewer_open():
            self._dataviewer.show_data_file(data_file)

    def _select_dir(self):
        new_dir = tkFileDialog.askdirectory()
        if new_dir:
            self._varDataFolder.set(new_dir)
        
    def _is_dataviewer_open(self):
        return self._dataviewer is not None and \
            self._dataviewer.window.winfo_exists()

    def _view_data(self):
        from dataviewer import data_viewer
        self._dataviewer = data_viewer(self._varDataFolder.get())


class PolpCycleControlUi(object):

    NMR_MODE = 'nmr'
    POL_MODE = 'pol'

    def __init__(self, parent):
        self._parent = parent
        self._varMode = StringVar(value=self.NMR_MODE)
        self._init_ui()

    def _init_ui(self):
        ttk.Label(self._parent, text='Polarization control:').grid(
            column=0, row=0, columnspan=2, sticky=W)
        self._rbtPolMode = ttk.Radiobutton(
            self._parent, text='Polarization mode',
            variable=self._varMode, value=self.POL_MODE)
        self._rbtPolMode.grid(column=0, row=1, sticky=W, padx=10, pady=5)
        self._rbtNmrMode = ttk.Radiobutton(
            self._parent, text='NMR mode',
            variable=self._varMode, value=self.NMR_MODE)
        self._rbtNmrMode.grid(column=0, row=2, sticky=W, padx=10, pady=5)
        self._varMode.trace('w', self._varMode_onchange)
        self._varMode.set(self.NMR_MODE)

    def _varMode_onchange(self, name, index, mode):
        logging.debug('mode selected: {}'.format(self._varMode.get()))
        if self._varMode.get() == self.NMR_MODE:
            polcontrol.mw_off()
        else:
            polcontrol.mw_on()


def _configure_logging():
    program_path = os.path.dirname(os.path.realpath(__file__))
    logging.config.fileConfig(os.path.join(program_path, 'logging.cfg'))


if __name__ == '__main__':
    start_app()
