############################################################
# UI front-end for polp:
#  - acquisition of NMR signals
#  - turn on polarization cycle (switch SPDT)
#
# all hardware functions are handled by respective utilities
# written separately from this module which only contains
# UI elements for user interaction
############################################################


from Tkinter import *
import ttk


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
        self._tk_root.title = 'Polp'

        self._init_frames()
        self._init_nmr_control_ui()
        self._init_polp_cycle_control_ui()

    def _init_frames(self):
        self._nmr_frame = ttk.Frame(self._tk_root, padding="3 3 12 12")
        self._nmr_frame.grid(column=0, row=0, sticky=(N, W, E, S))
        self._pol_frame = ttk.Frame(self._tk_root, padding="3 3 12 12")
        self._pol_frame.grid(column=1, row=0, sticky=(N, W, E, S))

    def _setup_layout(self):
        pass

    def _init_nmr_control_ui(self):
        self._nmr_control_ui = NmrControlUi(self._nmr_frame)

    def _init_polp_cycle_control_ui(self):
        self._polp_cycle_control_ui = PolpCycleControlUi(self._pol_frame)


class NmrControlUi(object):

    def __init__(self, parent):
        self._parent = parent
        self._init_ui()

    def _init_ui(self):
        ttk.Button(self._parent, text="NMR").grid(column=3, row=3, sticky=E)


class PolpCycleControlUi(object):

    def __init__(self, parent):
        self._parent = parent
        self._mode = StringVar()
        self._init_ui()

    def _init_ui(self):
        ttk.Radiobutton(self._parent, text='Polarization mode',
                        variable=self._mode, value='pol').grid(
                            column=0, row=0, sticky=W)
        ttk.Radiobutton(self._parent, text='NMR mode',
                        variable=self._mode, value='nmr').grid(
                            column=0, row=1, sticky=W)


if __name__ == '__main__':
    tk_root = Tk()
    polp_ui = PolpUi(tk_root)
    polp_ui.show()
