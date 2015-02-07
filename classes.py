__author__ = 'Adam Carlson'

import matplotlib
matplotlib.use('TkAgg')

from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg, NavigationToolbar2

class ActuallyWorkingFigureCanvas(FigureCanvasTkAgg):
    def rebinder(self):
        self._tkcanvas.bind("<Configure>", self.resize)
        self._tkcanvas.bind("<Key>", self.key_press)
        self._tkcanvas.bind("<Motion>", self.motion_notify_event)
        self._tkcanvas.bind("<KeyRelease>", self.key_release)
        for name in "<Button-1>", "<Button-2>", "<Button-3>":
            self._tkcanvas.bind(name, self.button_press_event)
        for name in "<Double-Button-1>", "<Double-Button-2>", "<Double-Button-3>":
            self._tkcanvas.bind(name, self.button_dblclick_event)
        for name in "<ButtonRelease-1>", "<ButtonRelease-2>", "<ButtonRelease-3>":
            self._tkcanvas.bind(name, self.button_release_event)

        # Mouse wheel on Linux generates button 4/5 events
        for name in "<Button-4>", "<Button-5>":
            self._tkcanvas.bind(name, self.scroll_event)
        # Mouse wheel for windows goes to the window with the focus.
        # Since the canvas won't usually have the focus, bind the
        # event to the window containing the canvas instead.
        # See http://wiki.tcl.tk/3893 (mousewheel) for details
        root = self._tkcanvas.winfo_toplevel()
        root.bind("<MouseWheel>", self.scroll_event_windows)

        # Can't get destroy events by binding to _tkcanvas. Therefore, bind
        # to the window and filter.
        def filter_destroy(evt):
            if evt.widget is self._tkcanvas:
                self.close_event()
        root.bind("<Destroy>", filter_destroy)

class ActuallyWorkingToolbar(NavigationToolbar2TkAgg):
    def __init__(self, canvas, window):
        NavigationToolbar2TkAgg.__init__(self, canvas, window)
        self.pButton = None
        self.hide()

    def hide(self, *args):
        Frame.pack_forget(self)

    def show(self):
        Frame.pack(self, side=TOP, fill=X, expand=0)

    def pan(self, *args):
        self.pButton = 'pan'
        NavigationToolbar2.pan(self, *args)

    def releasePan(self):
        self.pan()

    def zoom(self, *args):
        self.pButton = 'zoom'
        NavigationToolbar2.zoom(self, *args)

    def releaseZoom(self):
        self.zoom()

    def releaseButton(self):
        if self.pButton == 'pan':
            self.releasePan()
        if self.pButton == 'zoom':
            self.releaseZoom()