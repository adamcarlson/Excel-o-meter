__author__ = 'Adam Carlson'

import matplotlib
matplotlib.use('TkAgg')

from tkinter import Frame, Canvas, PhotoImage
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, FigureCanvasAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg, NavigationToolbar2

class ActuallyWorkingFigureCanvas(FigureCanvasTkAgg):
    def __init__(self, figure, master=None, resize_callback=None):
        FigureCanvasAgg.__init__(self, figure)
        self._idle = True
        self._idle_callback = None
        t1,t2,w,h = self.figure.bbox.bounds
        w, h = int(w), int(h)
        self._tkcanvas = Canvas(
            master=master, width=w, height=h, borderwidth=0)
        self._tkphoto = PhotoImage(
            master=self._tkcanvas, width=w, height=h)
        self._tkcanvas.create_image(w//2, h//2, image=self._tkphoto)
        self._resize_callback = resize_callback
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

        self._master = master

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
    def __init__(self, canvas, parent):
        self.parent = parent
        self.frame = Frame(parent)
        NavigationToolbar2TkAgg.__init__(self, canvas, self.frame)
        self.pButton = None
        Frame.pack(self)

        self.hide()

    def hide(self, *args):
        Frame.grid_remove(self.frame)
        self.releaseButton()

    def show(self, row):
        Frame.grid(self.frame, row=2, column=0, sticky='nsew')

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












#--------------------------------------- Unused, but for the future --------------------------------------

'''
    def draw4DGraph(self, graphFrame, sensorNum, sensorList):
        figure = plt.figure(dpi=100, frameon=False)
        canvas = classes.ActuallyWorkingFigureCanvas(figure, graphFrame)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        plot = Axes3D(figure)
        line = plot.plot([sensorList[X][0], sensorList[X][1]],
                         [sensorList[Y][0], sensorList[Y][1]],
                         [sensorList[Z][0], sensorList[Z][1]])[0]

        plot.set_xlim3d([0.0, 5.0])
        plot.set_xlabel('X')
        plot.set_ylim3d([0.0, 5.0])
        plot.set_ylabel('Y')
        plot.set_zlim3d([0.0, 5.0])
        plot.set_zlabel('Z')
        plot.set_title('Sensor {}'.format(sensorNum))

        anm.FuncAnimation(figure, self.update_lines, np.size(sensorList[X]), fargs=(sensorList, line), interval=1, blit=False)
        toolbar = classes.ActuallyWorkingToolbar(canvas, graphFrame)
        canvas.show()
        toolbar.update()
        toolbar.pack(side='top', fill='both')

        return figure

    def update_lines(self, num, data, line):
        if num > 20:
            x = num - 20
        else:
            x = 0
        line.set_data([data[0][i] for i in range(x, num)], [ data[1][i] for i in range(x, num)])
        line.set_3d_properties([data[2][i] for i in range(x, num)])
        return line


         self.selectorVar = StringVar(self.parent)
        self.selectorVar.set("xlsx")
        om = OptionMenu(self, self.selectorVar, "xlsx")
        om.configure(font=("Calibri", 16), fg=self.colorScheme['textNormal'], bg=self.colorScheme['bgNormal'])
        om.grid(row=1, column=0, sticky='nsew')

        self.sensorsVar = IntVar(self.parent)
        rbAll = Radiobutton(self, text='All', font=("Calibri", 16), selectcolor='#000000', bg=self.colorScheme['bgNormal'], fg=self.colorScheme['textNormal'], variable=self.sensorsVar, value=1, command=self.on_click)
        rbAll.grid(row=2, column=0, sticky='nsew')
        rbAll.select()
        rbSelect = Radiobutton(self, text='Select', font=("Calibri", 16), selectcolor='#000000', bg=self.colorScheme['bgNormal'], fg=self.colorScheme['textNormal'], variable=self.sensorsVar, value=2, command=self.on_click)
        rbSelect.grid(row=3, column=0, sticky='nsew')

        self.sensorList = [IntVar(self.parent) for i in range(3)]
        self.checkButtons = [Checkbutton(self, text='sensor {}'.format(i+1), font=("Calibri", 16), bg=self.colorScheme['bgNormal'], fg=self.colorScheme['textNormal'], variable=self.sensorList[i], state=DISABLED) for i in range(3)]
        for i, button in enumerate(self.checkButtons):
            button.grid(row=i+4, column=0, sticky='nsew')

        self.HzList = IntVar(self.parent)
        self.HzRadioList = [Radiobutton(self, text='{} Hz'.format(int(pow(2, 3-i)*100)), font=("Calibri", 16), bg=self.colorScheme['bgNormal'], fg=self.colorScheme['textNormal'], variable=self.HzList, value=i) for i in range(4)]
        for i, item in enumerate(self.HzRadioList):
            item.grid(row=i, column=2, sticky='nsew')

        Button(self, text="Export", font=("Calibri", 16), bg=self.colorScheme['bgNormal'], fg=self.colorScheme['textNormal'], command=self.export).grid(row=4, column=2, sticky='nsew')




'''