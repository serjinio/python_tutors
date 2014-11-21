

import os
import logging
import logging.config
import math
import numpy as np

from Tkinter import *
import tkFileDialog
import ttk

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import \
    FigureCanvasTkAgg, NavigationToolbar2TkAgg

from polpcommon import list_files_matching_extension, load_data_file


class DataViewerUi(object):

    def __init__(self, parent, folder=os.getcwd()):
        logging.debug('constructing data viewer for folder: "{}"'
                      .format(folder))
        self._parent = parent

        self._varCurrentDir = StringVar(value=folder)
        self._varFileList = StringVar()

        self._init_ui()
        self._load_file_list()

    def _init_ui(self):
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

        self._frmMpl = ttk.Frame(self._frame)
        self._mplFigure = Figure(figsize=(5, 4), dpi=100)
        self._cnvMplGraphView = FigureCanvasTkAgg(
            self._mplFigure, master=self._frmMpl)
        self._cnvMplGraphView.show()
        self._cnvMplGraphView.get_tk_widget().pack(
            side=TOP, fill=BOTH, expand=1)

        self._cnvMplGraphView_toolbar = NavigationToolbar2TkAgg(
            self._cnvMplGraphView, self._frmMpl)
        self._cnvMplGraphView_toolbar.update()

        self._parent.rowconfigure(0, weight=100)
        self._parent.columnconfigure(0, weight=100)
        self._frame.columnconfigure(1, weight=24)
        self._frame.columnconfigure(3, weight=75)
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
        self._frmMpl.grid(column=3, row=1, pady=5, padx=5,
                          sticky=(N, W, S, E))
        self._szGrip = ttk.Sizegrip(self._frame).grid(
            column=999, row=999, sticky=(S, E))

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
        logging.debug('will display data file: "{}"'.format(filepath))
        dataset = load_data_file(filepath)
        self.draw_plot(dataset)

    def draw_plot(self, dataset):
        self._mplFigure.clear()
        axes = self._mplFigure.add_subplot(111)
        self._plot_dataset(axes, dataset)
        self._mpl_setup_axes(axes, dataset)
        self._cnvMplGraphView.draw()

    def _mpl_setup_axes(self, ax, dataset):
        ax.set_title(dataset.title)
        ax.set_xlabel(dataset.x_data_name)
        ax.set_ylabel(dataset.y_data_name)
        ax.legend()
        ax.grid()

    def _plot_dataset(self, axes, dataset):
        if dataset.is_y_data_complex():
            real_part = [c.real for c in dataset.y_data]
            imag_part = [c.imag for c in dataset.y_data]
            axes.plot(dataset.x_data, real_part, label='Re')
            axes.plot(dataset.x_data, imag_part, label='Im')
        else:
            axes.plot(dataset.x_data, dataset.y_data)

    def draw_sample_graph(self):
        a = self._mplFigure.add_subplot(111)
        t = np.arange(0.0, 3.0, 0.01)
        s = np.sin(2 * math.pi * t)
        a.plot(t, s)
        a.set_title('Tk embedding')
        a.set_xlabel('X axis label')
        a.set_ylabel('Y label')


def _configure_logging():
    program_path = os.path.dirname(os.path.realpath(__file__))
    logging.config.fileConfig(os.path.join(program_path, 'logging.cfg'))


if __name__ == '__main__':
    _configure_logging()
    root = Tk()
    dv = DataViewerUi(root, '/mnt/hgfs/lab_data/2013/0919')
    dv.draw_sample_graph()
    root.mainloop()
