

import os
import logging
import logging.config

from Tkinter import *
import tkFileDialog
import ttk
from tkwidgets.plotting import PlotCanvas


from common import list_files_matching_extension, load_data_file, \
    INVALID_DATA_SET


def data_viewer(folder=os.getcwd(), parent=None):
    """Creates and shows DataViewer window.

    Args:
      folder (string): Folder at which to create data viewer.
      parent (Tk toplevel, optional): Parent window for this data viewer.
        Use when you want to specify your pre-existing window object to use
        for this data viewer.
    """
    DataViewerUi(folder, parent).show()


class DataViewerUi(object):

    def __init__(self, folder=os.getcwd(), parent=None):
        """Data viewer constructor.

        Args:
          folder (string): Folder at which to open data viewer.
          parent (Tk toplevel window, optional): Using this parameter you can
            optionally specify window object to use for this data viewer.
        """
        logging.debug('constructing data viewer for folder: "{}"'
                      .format(folder))
        self._parent = parent
        self._varCurrentDir = StringVar(value=folder)
        self._varFileList = StringVar()

    def show(self):
        if self._parent is None:
            self._parent = Toplevel()
        self._init_ui()
        self._load_file_list()

    def _init_ui(self):
        self._init_menu()
        self._frame = ttk.Frame(self._parent)

        self._btnChangeDir = ttk.Button(
            self._frame, text="Change Dir.", command=self._select_dir)
        self._entCurrentDir = ttk.Entry(
            self._frame, textvariable=self._varCurrentDir, width=25)
        self._entCurrentDir.configure(state='readonly')

        self._lstFiles = Listbox(self._frame,
                                 listvariable=self._varFileList)
        self._scrFiles = ttk.Scrollbar(self._frame, orient=VERTICAL,
                                       command=self._lstFiles.yview)
        self._lstFiles['yscrollcommand'] = self._scrFiles.set
        self._lstFiles.bind('<<ListboxSelect>>', self._lstFiles_onselect)
        self._lblDataView = ttk.Label(self._frame, text='Data View:')

        self._frmPlot = ttk.Frame(self._frame)
        self._pltCanvas = PlotCanvas(self._frmPlot)
        self._pltCanvas.pack(
            side=TOP, fill=BOTH, expand=1)

        self._parent.rowconfigure(0, weight=100)
        self._parent.columnconfigure(0, weight=100)
        self._frame.columnconfigure(1, weight=19)
        self._frame.columnconfigure(3, weight=80)
        self._frame.rowconfigure(1, weight=99)
        self._frame.grid(row=0, column=0, sticky=(N, W, E, S))
        self._btnChangeDir.grid(
            column=0, row=0, padx=5, pady=10, sticky=(N, W, E, S))
        self._entCurrentDir.grid(
            column=1, row=0, columnspan=2, padx=5, pady=10,
            sticky=(N, W, E, S))
        self._lblDataView.grid(
            column=3, row=0, pady=5, padx=5,
            sticky=(N, W, S, E))
        self._lstFiles.grid(column=0, columnspan=2, row=1, padx=5,
                            pady=5, sticky=(N, W, E, S))
        self._scrFiles.grid(column=2, row=1, pady=5, sticky=(N, S))
        self._frmPlot.grid(column=3, row=1, pady=5, padx=5,
                           sticky=(N, W, S, E))
        self._szGrip = ttk.Sizegrip(self._frame).grid(
            column=999, row=999, sticky=(S, E))

    def _init_menu(self):
        self._menubar = Menu(self._parent)
        self._parent['menu'] = self._menubar
        self._mnuFile = Menu(self._menubar)
        self._menubar.add_cascade(menu=self._mnuFile, label='File')
        self._mnuFile.add_command(label='Exit', command=self._exit)

    def _load_file_list(self):
        matching_file_list = list_files_matching_extension(
            self._varCurrentDir.get(), ['.dat', '.smd'])
        self._varFileList.set(tuple(matching_file_list))
        for i in range(0, len(matching_file_list), 2):
            self._lstFiles.itemconfigure(i, background='#f0f0ff')

    def _select_dir(self):
        new_dir = tkFileDialog.askdirectory()
        if new_dir:
            self._varCurrentDir.set(new_dir)
            self._load_file_list()

    def _lstFiles_onselect(self, evt):
        if len(evt.widget.curselection()) == 0:
            return
        index = int(evt.widget.curselection()[0])
        filename = evt.widget.get(index)
        filepath = os.path.join(self._varCurrentDir.get(), filename)
        dataset = self._load_dataset(filepath)
        self._draw_plot(dataset)

    def _load_dataset(self, filepath):
        try:
            return load_data_file(filepath)
        except ValueError:
            return INVALID_DATA_SET

    def _draw_plot(self, dataset):
        self._pltCanvas.clear()
        self._plot_dataset(self._pltCanvas, dataset)
        self._plot_setup_attrs(self._pltCanvas, dataset)

    def _plot_setup_attrs(self, canvas, dataset):
        pass
        # ax.set_title(dataset.title)
        # ax.set_xlabel(dataset.x_data_name)
        # ax.set_ylabel(dataset.y_data_name)
        # ax.legend()
        # ax.grid()

    def _plot_dataset(self, axes, dataset):
        if dataset.is_y_data_complex():
            real_part = [c.real for c in dataset.y_data]
            imag_part = [c.imag for c in dataset.y_data]
            axes.plot(dataset.x_data, real_part, label='Re')
            axes.plot(dataset.x_data, imag_part, label='Im')
        else:
            axes.plot(dataset.x_data, dataset.y_data)

    def _exit(self):
        self._parent.destroy()


def _configure_logging():
    program_path = os.path.dirname(os.path.realpath(__file__))
    logging.config.fileConfig(os.path.join(program_path, 'logging.cfg'))


if __name__ == '__main__':
    _configure_logging()
    root = Tk()
    data_viewer('/mnt/hgfs/lab_data/2013/0919', root)
    root.mainloop()
