"""
Visualizer module.
"""

import os
import logging
import logging.config

import matplotlib
matplotlib.use('TkAgg')
import Tkinter as tk
from matplotlib.backends.backend_tkagg import \
    FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import tkFileDialog
import ttk
import numpy as np
import pandas as pd

import common


def data_viewer(folder=os.getcwd()):
    """Creates and shows DataViewer window.

    Args:
      folder (string): Folder at which to create data viewer.
      parent (Tk toplevel, optional): Parent window for this data viewer.
        Use when you want to specify your pre-existing window object to use
        for this data viewer.
    """
    dv = DataViewer(tk.Tk())
    dv.show()
    return dv


class DataViewer(object):

    SHOW_ALL = 'show_all'
    SHOW_SELECTED = 'show_selected'

    def __init__(self, parent=None):
        """Data viewer constructor.

        Args:
          parent (Tk toplevel window, optional): Using this parameter you can
            optionally specify window object to use for this data viewer.
        """
        logging.debug('constructing data viewer')
        self.window = parent
        self._varShowMode = tk.StringVar(value=self.SHOW_ALL)
        self._varObjects = tk.StringVar()
        self._objects = {}

    def show(self):
        if self.window is None:
            self.window = tk.Toplevel()
        if hasattr(self, '_frame'):
            return
        self._init_ui()
        self._connect_events()

    def refresh(self):
        self._mplFigure.canvas.draw()

    def add_object(self, obj, name):
        """Adds new object to this data viewer."""
        self._lstObjects_additem(name)
        self._objects[name] = obj

    def remove_object(self, name):
        """Removes object by name."""
        del self._objects[name]
        self._lstObjects_removeobj(name)

    def _init_ui(self):
        self._init_menu()
        self._frame = ttk.Frame(self.window)
        self._panes = ttk.Panedwindow(self._frame, orient=tk.HORIZONTAL)
        self._leftPaneFrame = ttk.Frame(self._panes, width=100)
        self._rightPaneFrame = ttk.Frame(self._panes, width=300)
        self._panes.add(self._leftPaneFrame)
        self._panes.add(self._rightPaneFrame)

        self._lblShowData = ttk.Label(self._leftPaneFrame,
                                      text='Data objects:')
        self._lstObjects = tk.Listbox(self._leftPaneFrame,
                                      listvariable=self._varObjects,
                                      selectmode=tk.EXTENDED)
        self._scrFiles = ttk.Scrollbar(self._leftPaneFrame, orient=tk.VERTICAL,
                                       command=self._lstObjects.yview)
        self._lstObjects['yscrollcommand'] = self._scrFiles.set
        self._lblDataView = ttk.Label(self._rightPaneFrame, text='Data View:')

        self._frmPlot = ttk.Frame(self._rightPaneFrame)
        self._mplFigure = Figure(figsize=(5, 4), dpi=100)
        self._pltCanvas = FigureCanvasTkAgg(self._mplFigure,
                                            master=self._frmPlot)
        self._pltCanvas.show()
        self._pltCanvas.get_tk_widget().pack(
            side=tk.TOP, fill=tk.BOTH, expand=1)
        self._mplToolbar = NavigationToolbar2TkAgg(self._pltCanvas,
                                                   self._frmPlot)
        self._mplToolbar.update()
        self._pltCanvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self._leftPaneFrame.columnconfigure(0, weight=33)
        self._leftPaneFrame.columnconfigure(1, weight=33)
        self._leftPaneFrame.columnconfigure(2, weight=33)
        self._leftPaneFrame.rowconfigure(1, weight=99)
        self._lblShowData.grid(
            column=0, row=0, padx=5, pady=10, sticky=(tk.N, tk.W, tk.S))
        self._lstObjects.grid(column=0, columnspan=3, row=1, padx=5,
                              pady=5, sticky=(tk.N, tk.W, tk.E, tk.S))
        self._scrFiles.grid(column=50, row=1, pady=5, sticky=(tk.N, tk.S))

        self._rightPaneFrame.rowconfigure(1, weight=99)
        self._rightPaneFrame.columnconfigure(0, weight=99)
        self._lblDataView.grid(column=0, row=0, padx=5, pady=10,
                               sticky=(tk.W, tk.E))
        self._frmPlot.grid(column=0, row=1, sticky=(tk.N, tk.W, tk.S, tk.E))

        self._frame.columnconfigure(0, weight=100)
        self._frame.rowconfigure(0, weight=99)
        self._panes.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self._szGrip = ttk.Sizegrip(self._frame).grid(
            column=0, row=999, sticky=(tk.W, tk.E))
        self._frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def _connect_events(self):
        self._varShowMode.trace('w', self._varShowMode_onchange)
        self._lstObjects.bind('<<ListboxSelect>>', self._lstObjects_onselect)

    def _init_menu(self):
        self._menubar = tk.Menu(self.window)
        self.window['menu'] = self._menubar
        self._mnuFile = tk.Menu(self._menubar)
        self._menubar.add_cascade(menu=self._mnuFile, label='File')
        self._mnuFile.add_command(label='Exit', command=self._exit)

        self._mnuSamplePlots = tk.Menu(self._menubar)
        self._menubar.add_cascade(menu=self._mnuSamplePlots,
                                  label='Sample Plots')
        self._mnuSamplePlots.add_command(label='Sine',
                                         command=self._draw_sample_sine)

    def _varShowMode_onchange(self, name, index, mode):
        logging.debug('mode selected: {}'.format(self._varShowMode.get()))

    def _lstObjects_onselect(self, evt):
        logging.debug('objects selection change: {}'.
                      format(self._lstObjects.curselection()))
        self._mplFigure.clear()
        for idx in self._lstObjects.curselection():
            objname = self._lstObjects.get(idx)
            self._draw_object(self._objects[objname], objname)

    def _lstObjects_additem(self, itemname):
        self._lstObjects.insert(tk.END, itemname)
        for i in range(0, self._lstObjects.size(), 2):
            self._lstObjects.itemconfigure(i, background='#f0f0ff')

    def _lstObjects_removeobj(self, itemname):
        for idx, el in enumerate(self._lstObjects.get(0, tk.END)):
            if el == itemname:
                self._lstObjects.delete(idx)
                break

    def _draw_object(self, obj, name):
        ax = self._mplFigure.add_subplot('111')
        self._draw_pd_dataframe(obj, name, ax)
        ax.legend()
        self.refresh()

    def _draw_pd_dataframe(self, df, name, axes):
        logging.debug('drawing dataset: "{}"'.format(name))
        if len(df) == 0:
            logging.warn('attemted to draw an empty dataset: "{}"'
                         .format(name))
            return
        for c in df.columns:
            if isinstance(df[c][df.index[0]], complex):
                axes.plot(df.index, np.real(df[c]),
                          label=name + " - Re(" + str(c) + ")")
                axes.plot(df.index, np.imag(df[c]),
                          label=name + " - Im(" + str(c) + ")")
            else:
                axes.plot(df.index, df[c], label=name + " - " + str(c))

    def _draw_sample_sine(self):
        args = np.arange(1000.)
        df = pd.DataFrame(np.sin(np.radians(args)), index=args, columns=['y'])
        self.add_object(df, 'sin(x)')

    def _exit(self):
        self.window.destroy()


if __name__ == '__main__':
    common.configure_logging()
    root = tk.Tk()
    data_viewer(root)
    root.mainloop()
