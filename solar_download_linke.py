
"""
DOWNLOAD LINKE TURBIDITY COEFFICIENT TOOL
A Python script that downloads Linke turbidity coefficient values
from the SoDA (Solar Radiation Data) webservice (www.soda-is.com)
into a .csv file.

The output .csv file is header-less with the following format
(LON, LAT, JAN, FEB, MAR, APR, MAY, JUN, JUL, AUG, SEP, OCT, NOV, DEC).

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
except ImportError:
    import tkinter as tk
    import tkinter.ttk as ttk
    from tkinter.constants import *

import solar_download_linke_gui


T_WIDTH = 480
T_HEIGHT = 480


def main():
    root = tk.Tk()
    root.title('REMap Solar Download Utilities')
    icon = tk.Image('photo', file='imgs/Solar.png')
    root.tk.call('wm', 'iconphoto', root._w, icon)
    root.geometry('{}x{}'.format(T_WIDTH, T_HEIGHT))
    root.resizable(width=FALSE, height=FALSE)

    nb = ttk.Notebook(root,
                      height=T_HEIGHT-90)
    linke = solar_download_linke_gui.DownloadLinkeApp(nb)
    nb.add(linke, text="Linke Turbidity", sticky=E+W)

    # asti = solar_download_asti_gui.DownloadSensorApp(nb)
    # nb.add(asti, text="ASTI Sensor Data", sticky=E+W)
    nb.grid(row=0, column=0)


    menubar = tk.Menu(root)
    aboutmenu = tk.Menu(menubar, tearoff=0)
    aboutmenu.add_command(label="README", command=show_readme)
    # aboutmenu.add_command(label="ABOUT", command=show_about)
    # aboutmenu.add_command(label="REMap|SOLAR", command=show_solar)
    menubar.add_cascade(label='About', menu=aboutmenu)
    root.config(menu=menubar)

    decor = tk.Frame(root)
    decor.grid(row=1, sticky=N+E+W+S)
    logo = tk.Image('photo', file='imgs/Solar.png')
    logoLabel = tk.Label(decor,
                         height=64,
                         width=64,
                         relief=RAISED,
                         background='white',
                         image=logo)
    logoLabel.grid()

    root.mainloop()


def show_readme():
    top = tk.Toplevel()
    top.title("README")
    top.resizable(width=FALSE, height=FALSE)
    msg = tk.Message(top, text=__doc__)
    msg.pack()

# def show_about():
#     pass

# def show_solar():
#     pass



# TEST MAIN
if __name__ == '__main__':
    main()