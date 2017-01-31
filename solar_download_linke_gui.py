"""
The SOLAR download tool is a collection of scripts that includes:

1.) DOWNLOAD LINKE TURBIDITY COEFFICIENT TOOL
A Python script that downloads Linke turbidity coefficient values
from the SoDA (Solar Radiation Data) webservice (www.soda-is.com)
into a .csv file.

The output .csv file is header-less with the following format
(LON, LAT, JAN, FEB, MAR, APR, MAY, JUN, JUL, AUG, SEP, OCT, NOV, DEC).

2.) DOWNLOAD ASTI SENSOR DATA
A Python script that scrapes daily measurements from weather stations in
the DOST ASTI (Advanced Science and Technology Institute) database.


NB:
The Tool has only been tested for *buntu (Linux) OS and Python 2.7
The requirements/modules used are found in the included requirements.txt
This Tool is provided under the GNU General Public License v3.0.

Copyright (C) 2015 Ben Hur S. Pintor

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Ben Hur S. Pintor"
__contact__ = "bhs.pintor<at>gmail.com"

try:
    import Tkinter as tk
    import ttk
    from Tkconstants import *
    import tkFileDialog as filedialog
    # import tkFont as font

except ImportError:
    import tkinter as tk
    import tkinter.ttk as ttk
    from tkinter.constants import *
    import tkinter.filedialog as filedialog
    # import tkinter.font as font

import solar_download_linke_utils

# FONTS
RADIOBUTTON_FONT = ('Times New Roman', 12)
BANNER_FONT = ('Times New Roman', 16)
LABEL_FONT = ('Arial', 10)
ENTRY_FONT = ('Arial', 10)
TOOLTIP_FONT = ('Arial', 9)

ROOT_WIDTH = 480
ROOT_HEIGHT = 480

# TOOLTIPS
SELECTDEM_TT = """Select the DEM (.tif) to use for determining the extent 
to download the Linke turbidity coefficients."""

EPSG_TT = """Enter the EPSG Code of Coordinate System of the DEM.

Commonly used EPSG Codes:
4326  - WGS84
32651 - WGS84/UTM Zone 51N"""

INTERVAL_TT="""Enter the interval (in decimal degrees)
between successive Linke turbidity coefficient downloads"""

SELECTTXT_TT = """Select the text (.txt) file containing coordinates formatted
as longitude, latitude in the WGS84 coordinate system"""

BOUND_TT = "The %s (decimal degrees) of the %s edge of the bounding box"

PROXY_TT = "Enter the proxy server (if any)"

PORT_TT = "Enter the proxy port (if any)"

SELECTSAVE_TT = "Select the save file (.csv) to download the Linke turbidity values to"

class ToolTip(object):
    """
    A class that creates a tooltip for a given widget when the mouse hovers
    over the widget.
    """

    def __init__(self, widget, tip="INFO"):
        """Initializes the tooltip.
        :param widget: the widget to attach the tooltip to
        :param tip: a string of the tip to be shown when the mouse is over the widget
        """

        self.widget = widget
        self.tip = tip
        self.widget.bind('<Enter>', self.enter)
        self.widget.bind('<Leave>', self.close)

    def enter(self, event=None):
        """Handles what happens when the mouse is over the widget"""
        x = y = 0
        x, y, cx, cy = self.widget.bbox('insert')
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        # Create a Toplevel window
        self.top = tk.Toplevel(self.widget)

        # Removes the app window of the Toplevel window
        self.top.wm_overrideredirect(True)
        self.top.wm_geometry('+%d+%d' %(x, y))
        label = tk.Label(self.top, text=self.tip, justify='left', background='#87CEFA',
                         relief='solid', borderwidth=1, font=TOOLTIP_FONT)
        label.pack(ipadx=1)

    def close(self, event=None):
        """Handles what happens when the mouse leaves the widget"""
        if self.top:
            self.top.destroy()


class DownloadLinkeApp(tk.Frame):
    """A class for the Download Linke Turbidity Tool GUI"""

    def __init__(self, master=None):
        tk.Frame.__init__(self, master, width=ROOT_WIDTH, height=ROOT_HEIGHT)
        self.grid()

        '''Variables'''
        self.optionVar = tk.IntVar()
        self.optionVar.set(0)
        self.demPathVar = tk.StringVar()
        self.demPathVar.set('')
        self.txtPathVar = tk.StringVar()
        self.txtPathVar.set('')
        self.saveModeVar = tk.StringVar()
        self.saveModeVar.set('w')
        self.savePathVar = tk.StringVar()
        self.savePathVar.set('')

        '''Widgets'''
        self.headMast = tk.Label(self,
                                 text='Download Linke Turbidity',
                                 width=42,
                                 relief=RIDGE,
                                 borderwidth=2,
                                 background='yellow',
                                 font=BANNER_FONT)
        self.headMast.grid(row=0, sticky=N+E+W)

        # OPTION0 - DEM
        self.option0 = tk.Radiobutton(self,
                                      text='Use DEM to get extent',
                                      variable=self.optionVar,
                                      value=0,
                                      command=self.select_options,
                                      indicatoron=1,
                                      relief=RAISED,
                                      overrelief=SUNKEN,
                                      activebackground='yellow',
                                      anchor=W,
                                      font=RADIOBUTTON_FONT)
        self.option0.grid(row=1, sticky=N+E+W)

        self.option0Frame = tk.Frame(self,
                                     relief=RIDGE,
                                     borderwidth=2,
                                     width=ROOT_WIDTH-2,
                                     padx=1)
        self.option0Frame.grid(row=2, sticky=N+E+W+S)

        self.selectDEMBtn = tk.Button(self.option0Frame,
                                      text="Select DEM",
                                      command=self.select_dem,
                                      width=14,
                                      pady=2,
                                      padx=1,
                                      font=LABEL_FONT)
        self.selectDEMBtn.grid(row=0, sticky=E+W)
        self.demPath = tk.Entry(self.option0Frame,
                                textvariable=self.demPathVar,
                                readonlybackground='white',
                                state='readonly',
                                width=52,
                                font=ENTRY_FONT)
        self.demPath.grid(row=0, column=1, columnspan=3, sticky=E+W)
        self.selectDEMTT = ToolTip(self.selectDEMBtn,
                                   SELECTDEM_TT)

        self.epsgLabel = tk.Label(self.option0Frame,
                                  text='EPSG Code',
                                  relief=GROOVE,
                                  width=14,
                                  pady=2,
                                  padx=2,
                                  font=LABEL_FONT)
        self.epsgLabel.grid(row=1, column=0, sticky=E+W)
        self.epsgEntry = tk.Entry(self.option0Frame,
                                  width=18,
                                  font=ENTRY_FONT)
        self.epsgEntry.grid(row=1, column=1, sticky=E+W)
        self.epsgTT = ToolTip(self.epsgEntry,
                              EPSG_TT)

        self.interval0Label = tk.Label(self.option0Frame,
                                       text='Interval',
                                       relief=GROOVE,
                                       width=14,
                                       pady=2,
                                       padx=2,
                                       font=LABEL_FONT)
        self.interval0Label.grid(row=1, column=2, sticky=E+W)
        self.interval0Entry = tk.Entry(self.option0Frame,
                                       width=18,
                                       font=ENTRY_FONT)
        self.interval0Entry.grid(row=1, column=3, sticky=E+W)
        self.interval0TT = ToolTip(self.interval0Entry,
                                   INTERVAL_TT)

        # OPTION1 - TXT
        self.option1 = tk.Radiobutton(self,
                                      text='Use a text file of coordinates',
                                      variable=self.optionVar,
                                      value=1,
                                      command=self.select_options,
                                      indicatoron=1,
                                      relief=RAISED,
                                      overrelief=SUNKEN,
                                      activebackground='yellow',
                                      anchor=W,
                                      font=RADIOBUTTON_FONT)
        self.option1.grid(row=3, sticky=N+E+W)

        self.option1Frame = tk.Frame(self,
                                     relief=RIDGE,
                                     borderwidth=2,
                                     width=ROOT_WIDTH-2,
                                     padx=1)
        self.option1Frame.grid(row=4, sticky=N+E+W+S)

        self.selectTxtBtn = tk.Button(self.option1Frame,
                                      text="Select TXT",
                                      command=self.select_txt,
                                      width=14,
                                      pady=2,
                                      padx=1,
                                      font=LABEL_FONT)
        self.selectTxtBtn.grid(row=0, sticky=E+W)
        self.txtPath = tk.Entry(self.option1Frame,
                                textvariable=self.txtPathVar,
                                readonlybackground='white',
                                state='readonly',
                                width=52,
                                font=ENTRY_FONT)
        self.txtPath.grid(row=0, column=1, columnspan=3, sticky=E+W)
        self.selectTxtTT = ToolTip(self.selectTxtBtn,
                                   SELECTTXT_TT)

        # OPTION2 - BOUNDING BOX
        self.option2 = tk.Radiobutton(self,
                                      text='Use a bounding box to define extent',
                                      variable=self.optionVar,
                                      value=2,
                                      command=self.select_options,
                                      indicatoron=1,
                                      relief=RAISED,
                                      overrelief=SUNKEN,
                                      activebackground='yellow',
                                      anchor=W,
                                      font=RADIOBUTTON_FONT)
        self.option2.grid(row=5, sticky=N+E+W)

        self.option2Frame = tk.Frame(self,
                                     relief=RIDGE,
                                     borderwidth=2,
                                     width=ROOT_WIDTH-2,
                                     padx=1)
        self.option2Frame.grid(row=6, sticky=N+E+W+S)
        
        self.sLabel = tk.Label(self.option2Frame,
                               text='South',
                               relief=GROOVE,
                               width=14,
                               pady=2,
                               padx=2,
                               font=LABEL_FONT)
        self.sLabel.grid(row=0,column=0,sticky=E+W)
        self.sEntry = tk.Entry(self.option2Frame,
                               width=18,
                               font=ENTRY_FONT)
        self.sEntry.grid(row=0, column=1, sticky=E+W)
        self.sBoundTT = ToolTip(self.sEntry,
                                BOUND_TT %("LATITUDE", "SOUTH"))

        self.nLabel = tk.Label(self.option2Frame,
                               text='North',
                               relief=GROOVE,
                               width=14,
                               pady=2,
                               padx=2,
                               font=LABEL_FONT)
        self.nLabel.grid(row=0,column=2,sticky=E+W)
        self.nEntry = tk.Entry(self.option2Frame,
                               width=18,
                               font=ENTRY_FONT)
        self.nEntry.grid(row=0, column=3, sticky=E+W)
        self.nBoundTT = ToolTip(self.nEntry,
                                BOUND_TT %("LATITUDE", "NORTH"))

        self.wLabel = tk.Label(self.option2Frame,
                               text='West',
                               relief=GROOVE,
                               width=14,
                               pady=2,
                               padx=2,
                               font=LABEL_FONT)
        self.wLabel.grid(row=1,column=0,sticky=E+W)
        self.wEntry = tk.Entry(self.option2Frame,
                               width=18,
                               font=ENTRY_FONT)
        self.wEntry.grid(row=1, column=1, sticky=E+W)
        self.wBoundTT = ToolTip(self.wEntry,
                                BOUND_TT %("LONGITUDE", "WEST"))

        self.eLabel = tk.Label(self.option2Frame,
                               text='East',
                               relief=GROOVE,
                               width=14,
                               pady=2,
                               padx=2,
                               font=LABEL_FONT)
        self.eLabel.grid(row=1,column=2,sticky=E+W)
        self.eEntry = tk.Entry(self.option2Frame,
                               width=18,
                               font=ENTRY_FONT)
        self.eEntry.grid(row=1, column=3, sticky=E+W)
        self.eBoundTT = ToolTip(self.eEntry,
                                BOUND_TT %("LONGITUDE", "EAST"))

        self.interval2Label = tk.Label(self.option2Frame,
                                       text='Interval',
                                       relief=GROOVE,
                                       width=14,
                                       pady=2,
                                       padx=2,
                                       font=LABEL_FONT)
        self.interval2Label.grid(row=2,column=0,sticky=E+W)
        self.interval2Entry = tk.Entry(self.option2Frame,
                                       width=18,
                                       font=ENTRY_FONT)
        self.interval2Entry.grid(row=2, column=1, sticky=E+W)
        self.interval2TT = ToolTip(self.interval2Entry,
                                   INTERVAL_TT)

        # DOWNLOAD OPTIONS
        self.downloadOptionsFrame = tk.Frame(self,
                                             relief=RIDGE,
                                             borderwidth=2,
                                             width=ROOT_WIDTH-2,
                                             padx=1)
        self.downloadOptionsFrame.grid(row=7, column=0, sticky=E+W)

        self.downloadOptionsLabel = tk.Label(self.downloadOptionsFrame,
                                             text='Download Options',
                                             anchor=W,
                                             font=RADIOBUTTON_FONT)
        self.downloadOptionsLabel.grid(row=0, column=0, columnspan=5, sticky=E+W)

        self.proxyLabel = tk.Label(self.downloadOptionsFrame,
                                   text='Proxy',
                                   relief=GROOVE,
                                   width=14,
                                   pady=2,
                                   padx=2,
                                   font=LABEL_FONT)
        self.proxyLabel.grid(row=1, column=0, sticky=E+W)
        self.proxyEntry = tk.Entry(self.downloadOptionsFrame,
                                   width=33,
                                   font=ENTRY_FONT)
        self.proxyEntry.grid(row=1, column=1, columnspan=2, sticky=E+W)
        self.proxyTT = ToolTip(self.proxyEntry,
                               PROXY_TT)

        self.portLabel = tk.Label(self.downloadOptionsFrame,
                                  text='Port',
                                  relief=GROOVE,
                                  width=9,
                                  pady=2,
                                  padx=2,
                                  font=LABEL_FONT)
        self.portLabel.grid(row=1, column=3, sticky=E+W)
        self.portEntry = tk.Entry(self.downloadOptionsFrame,
                                  width=8,
                                  font=ENTRY_FONT)
        self.portEntry.grid(row=1, column=4, columnspan=2, sticky=E+W)
        self.portTT = ToolTip(self.portEntry,
                              PORT_TT)

        self.overwriteSave = tk.Radiobutton(self.downloadOptionsFrame,
                                            text="Overwrite Save File",
                                            width=26,
                                            variable=self.saveModeVar,
                                            value='w',
                                            relief=RAISED,
                                            overrelief=SUNKEN)
        self.overwriteSave.grid(row=2, column=0, columnspan=2, sticky=E+W)

        self.appendSave = tk.Radiobutton(self.downloadOptionsFrame,
                                         text="Append to Save File",
                                         width=26,
                                         variable=self.saveModeVar,
                                         value='a',
                                         relief=RAISED,
                                         overrelief=SUNKEN)
        self.appendSave.grid(row=2, column=2, columnspan=3, sticky=E+W)
        self.saveFileBtn = tk.Button(self.downloadOptionsFrame,
                                     text="Save File",
                                     command=self.select_save,
                                     width=14,
                                     pady=2,
                                     padx=2,
                                     font=LABEL_FONT)
        self.saveFileBtn.grid(row=3, column=0, sticky=E+W)
        self.savePath = tk.Entry(self.downloadOptionsFrame,
                                 textvariable=self.savePathVar,
                                 readonlybackground='white',
                                 state='readonly',
                                 width=50,
                                 font=ENTRY_FONT)
        self.savePath.grid(row=3, column=1, columnspan=4, sticky=E+W)
        self.savePathTT = ToolTip(self.saveFileBtn,
                                  SELECTSAVE_TT)

        self.downloadBtn = tk.Button(self.downloadOptionsFrame,
                                     text="DOWNLOAD LINKE",
                                     command=self.download_linke,
                                     width=26,
                                     height=1,
                                     font=RADIOBUTTON_FONT,
                                     activebackground='yellow')
        self.downloadBtn.grid(row=4, column=0, columnspan=2, sticky=E+W)

        self.select_options()

    def select_options(self):
        opt = self.optionVar.get()
        optFrames = [self.option0Frame, self.option1Frame, self.option2Frame]

        for child in optFrames[opt].winfo_children():
            child.config(state=NORMAL)

        del optFrames[opt]
        for optFrame in optFrames:
            for child in optFrame.winfo_children():
                child.config(state=DISABLED)

        for radButton in [self.option0, self.option1, self.option2]:
            radButton.config(state=NORMAL)

        self.set_readonly_entries(opt)

        self.update()

    def set_readonly_entries(self, opt):
        if opt == 0:
            self.demPath.config(state='readonly')

        if opt == 1:
            self.txtPath.config(state='readonly')

        self.update()

    def deactivate_all(self):
        for optFrame in [self.option0Frame, self.option1Frame, self.option2Frame]:
            for child in optFrame.winfo_children():
                child.config(state=DISABLED)

        for radButton in [self.option0, self.option1, self.option2]:
            radButton.config(state=DISABLED)

        self.update()

    def select_dem(self):
        dem = filedialog.askopenfilename(parent=self,
                                         filetypes=[('GTiff', '.tif')],
                                         title='Select DEM to determine extent')

        if dem is None:
            self.demPathVar.set('')
        else:
            self.demPathVar.set(dem)

    def select_txt(self):
        txt = filedialog.askopenfilename(parent=self,
                                         filetypes=[('text', '.txt')],
                                         title='Select text file of coordinates')

        if txt is None:
            self.txtPathVar.set('')
        else:
            self.txtPathVar.set(txt)

    def select_save(self):
        save = filedialog.asksaveasfilename(parent=self,
                                            filetypes=[('CSV', '.csv')],
                                            title='Select save file for Linke turbidity values')
        if save is None:
            self.savePathVar.set('')
        else:
            self.savePathVar.set(save)

    def download_linke(self):
        opt = self.optionVar.get()
        proxy = self.proxyEntry.get().strip()
        port = self.portEntry.get().strip()
        saveFile = self.savePathVar.get().strip()
        saveMode = self.saveModeVar.get().strip()

        # print opt, proxy, port, saveFile, saveMode

        try:
            if opt == 0:
                dem = self.demPathVar.get()
                crs = self.epsgEntry.get().strip()
                interval = float(self.interval0Entry.get().strip())
                coords = solar_download_linke_utils.get_extent_of_DEM(dem,
                                                                      crs,
                                                                      interval)
                self.deactivate_all()
                solar_download_linke_utils.download_linke(coords, proxy, port, saveFile, saveMode)

            if opt == 1:
                coords = []
                with open(self.txtPathVar.get(), 'r') as f:
                    for line in f.readlines():
                        line0 = line.strip('\n')
                        line1 = line0.split(',')
                        coords.append((float(line1[0]),float(line1[1])))
                self.deactivate_all()
                solar_download_linke_utils.download_linke(coords, proxy, port, saveFile, saveMode)

            if opt == 2:
                w = float(self.wEntry.get().strip())
                e = float(self.eEntry.get().strip())
                s = float(self.sEntry.get().strip())
                n = float(self.nEntry.get().strip())
                i = float(self.interval2Entry.get().strip())
                coords = [(w + (x*i), s + (y*i)) for x in range(int((e - w)/i)+1) for y in range(int((n - s)/i)+1)]
                self.deactivate_all()
                solar_download_linke_utils.download_linke(coords, proxy, port, saveFile, saveMode)

        except Exception as e:
            self.select_options()
            self.update()
        
        self.select_options()
        self.update()


def config_widget(widget, options):
    for key in options:
        widget[key] = options.get(key)
