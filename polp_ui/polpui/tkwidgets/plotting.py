"""
Contains plotting functionality using Tk canvas widget.
"""


import Tkinter
import logging

from polpui.common import DataSet


class PlotCanvasSettings(object):
    """Contains setting for PlotCanvas."""

    def __init__(self):
        """No arg constructor creates default settings object."""
        self.bg_color = '#ffffff'
        self.margins = 0.1
        self.axes_margins = self.margins / 2.
        self.grid = True


DEFAULT_PLOT_SETTINGS = PlotCanvasSettings()


class PlotCanvas(Tkinter.Canvas, object):

    def __init__(self, parent, cnf={},
                 plot_settings=DEFAULT_PLOT_SETTINGS, *kwargs):
        Tkinter.Canvas.__init__(self, parent, cnf, *kwargs)
        self._parent = parent
        self.plots = []
        self._plot_settings = plot_settings
        self._configure_canvas()

    def plot(self, x_data, y_data, label=None, xlabel=None, ylabel=None):
        plot = Plot(DataSet(x_data, y_data, label,
                            x_data_name=xlabel, y_data_name=ylabel))
        logging.debug('adding new plot: {}'.format(plot))
        self.plots.append(plot)
        self.refresh()

    def clear(self):
        self.plots = []
        self.refresh()

    def refresh(self):
        self.delete(Tkinter.ALL)
        self._draw_axes()
        self._draw_plots()

    def _configure_canvas(self):
        self.config(background=self._plot_settings.bg_color)
        self.bind('<Configure>', self._resize)

    def _resize(self, evt):
        self.refresh()

    def _draw_axes(self):
        ymin, ymax = self._plot_ylimits()
        ydist = abs(ymin - ymax)
        xmin, xmax = self._plot_xlimits()
        xdist = abs(xmax - xmin)
        ymin -= ydist * self._plot_settings.margins / 2.
        ymax += ydist * self._plot_settings.margins / 2.
        xmin -= xdist * self._plot_settings.margins / 2.
        xmax += xdist * self._plot_settings.margins / 2.
        ax = Axes((xmin, xmax), (ymin, ymax))
        ax.draw(self, self._drawing_prefs())

    def _draw_plots(self):
        draw_prefs = self._drawing_prefs()
        logging.debug('drawing plots using draw prefs: \n{}'.
                      format(draw_prefs))
        for p in self.plots:
            p.draw(self, draw_prefs)

    def _drawing_prefs(self):
        canvas_ylimits = (0, float(self.winfo_height()))
        canvas_xlimits = (0, float(self.winfo_width()))
        plot_ylimits = self._plot_ylimits()
        plot_xlimits = self._plot_xlimits()
        scaling = 1. - 2 * self._plot_settings.margins
        return DrawingPreferences(plot_xlimits, plot_ylimits,
                                  canvas_xlimits, canvas_ylimits,
                                  scale_factor=scaling)

    def _plot_ylimits(self):
        min_y, max_y = None, None
        for p in self.plots:
            lims = p.ylimits()
            if min_y is None:
                min_y = lims[0]
                max_y = lims[1]
                continue
            if lims[0] < min_y:
                min_y = lims[0]
            if lims[1] > max_y:
                max_y = lims[1]
        if min_y is None:
            min_y = -1.
        if max_y is None:
            max_y = 1.
        return (min_y, max_y)

    def _plot_xlimits(self):
        min_x, max_x = None, None
        for p in self.plots:
            lims = p.xlimits()
            if min_x is None:
                min_x = lims[0]
                max_x = lims[1]
                continue
            if lims[0] < min_x:
                min_x = lims[0]
            if lims[1] > max_x:
                max_x = lims[1]
        if min_x is None:
            min_x = -1.
        if max_x is None:
            max_x = 1.
        return (min_x, max_x)

    def __str__(self):
        plots_str = ''
        for p in self._plots:
            plots_str = str(p) + '\n'
        res = 'PlotCanvas, plots list: \n"{}"'.format(plots_str)
        return res


class Axes(object):
    """Axes on a drawing canvas."""

    def __init__(self, xlimits, ylimits):
        """Consturcts new axes instance.

        Args:
          xlimits (2-tuple): limits for X axis in plot coordinates
          ylimits (2-tuple): limits for Y axis in plot coordinates
        """
        self._xlimits = xlimits
        self._ylimits = ylimits

    def draw(self, plot_canvas, draw_prefs):
        x_origin, y_origin = self._xlimits[0], self._ylimits[0]
        x_top, y_top = self._xlimits[1], self._ylimits[1]
        x_origin_canv, y_origin_canv = draw_prefs.plot_point(
            x_origin, y_origin)
        x_top_canv, y_top_canv = draw_prefs.plot_point(
            x_top, y_top)
        logging.debug(('drawing axes at points: origin: {}:{}, '
                       'X,Y top: {}:{}').format(
                           x_origin, y_origin, x_top, y_top))
        logging.debug(('in canvas coordinates: origin: {}:{}, '
                       'X,Y top: {}:{}').format(
                           x_origin_canv, y_origin_canv,
                           x_top_canv, y_top_canv))
        plot_canvas.create_line(x_origin_canv, y_origin_canv,
                                x_origin_canv, y_top_canv, width=2.)
        plot_canvas.create_line(x_origin_canv, y_origin_canv,
                                x_top_canv, y_origin_canv, width=2.)


class Plot(object):
    """Represents plot on a PlotCanvas."""

    def __init__(self, dataset):
        """
        Args:
          dataset: A DataSet object containing data points to plot
        """
        self._dataset = dataset

    def draw(self, plot_canvas, draw_prefs):
        """Draws this plot into canvas.

        Args:
          plotCanvas (PlotCanvas): A plotting canvas to draw into.
        """
        logging.debug('drawing "{}" dataset...'.format(self._dataset.title))
        prev_x, prev_y = None, None
        for x, y in draw_prefs.plot_points(
                self._dataset.x_data, self._dataset.y_data):
            if prev_x is None:
                prev_x, prev_y = x, y
                continue
            plot_canvas.create_line(prev_x, prev_y, x, y)
            prev_x, prev_y = x, y

    def xlimits(self):
        """Return min & max X coordinates on this plot."""
        if len(self._dataset) > 1:
            return self._dataset.xlimits()
        else:
            return (-1.0, 1.0)

    def ylimits(self):
        """Return min & max Y coordinates on this plot."""
        if len(self._dataset) > 1:
            return self._dataset.ylimits()
        else:
            return (-1.0, 1.0)

    def __str__(self):
        res = 'Plot of : {}.'.format(self._dataset)
        return res


class DrawingPreferences(object):
    """Holds drawing settings pertaining to PlotCanvas."""

    def __init__(self,
                 plot_xlimits=(1., -1.), plot_ylimits=(1., -1.),
                 draw_xlimits=(1., -1.), draw_ylimits=(1., -1.),
                 scale_factor=1.0):
        self.plot_xlimits = plot_xlimits
        self.plot_ylimits = plot_ylimits
        self.draw_xlimits = draw_xlimits
        self.draw_ylimits = draw_ylimits
        self.scale_factor = scale_factor
        self._init_factors()

    def plot_points(self, x_data, y_data):
        plot_pts = []
        for x, y in zip(x_data, y_data):
            plot_pts.append((self.plot_x_coord(x), self.plot_y_coord(y)))
        return plot_pts

    def plot_point(self, x, y):
        """Returns 2-tuple with coordinates of canvas_point, where
        the provided data_point should be drawn.

        Args:
          data_point (2-tuple): X, Y coordinates of a data point which
            which coordinates need to be converted into canvas coordinates.
        """
        return (self.plot_x_coord(x), self.plot_y_coord(y))

    def plot_x_coord(self, x):
        """Returns plot X coordinate which corresponds to passed
        data X coordinate.
        """
        plot_x = (x * self._plot2draw_xfactor * self.scale_factor)
        plot_x += ((1. - self.scale_factor) / 2.) * self.draw_width
        return plot_x

    def plot_y_coord(self, y):
        """Returns plot Y coordinate which corresponds to passed
        data Y coordinate."""
        plot_y = (y * self._plot2draw_yfactor) + (self.draw_height / 2)
        plot_y *= self.scale_factor
        plot_y += ((1. - self.scale_factor) / 2.) * self.draw_height
        return plot_y

    def _init_factors(self):
        self.draw_width = abs(self.draw_xlimits[1] - self.draw_xlimits[0])
        self.draw_height = abs(self.draw_ylimits[1] - self.draw_ylimits[0])
        self.plot_width = abs(self.plot_xlimits[1] - self.plot_xlimits[0])
        self.plot_height = abs(self.plot_ylimits[1] - self.plot_ylimits[0])
        self._plot2draw_yfactor = self.draw_height / self.plot_height
        self._plot2draw_xfactor = self.draw_width / self.plot_width

    def __str__(self):
        res = 'Drawing preferences:\n'
        res += '\t Plot data X limits: {}:{}\n'.format(*self.plot_xlimits)
        res += '\t Plot data Y limits: {}:{}\n'.format(*self.plot_ylimits)
        res += '\t Drawing cordinates X limits: {}:{}\n'.format(
            *self.draw_xlimits)
        res += '\t Drawing cordinates Y limits: {}:{}\n'.format(
            *self.draw_ylimits)
        res += '\t Scaling factor: {}'.format(self.scale_factor)
        return res
