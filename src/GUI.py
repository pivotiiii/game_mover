import tkinter as tk
import os
import sys
from ctypes import windll, byref, sizeof, c_int
from MainFrame import MainFrame
from Config import Config
import Globals as g

#TODO
#handle game folder in both zB steamworks shared
#shouldnt be able to move folder or parent of folder that is added
#cant remove folder if junction points somewhere else

g.debug = False

class MainWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.near_exe_path = os.path.dirname(os.path.abspath(sys.argv[0]))   #for files in the same folder as the .exe created by nuitka
        self.in_exe_path = os.path.dirname(os.path.abspath(__file__))        #for files that should be included in the .exe (e.g. the icon)
        self.config_json = os.path.join(self.near_exe_path, "game_mover.json")

        g.config = Config(self.config_json)

        self.title("Game Mover")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        g.init_font()

        w = g.measure_in_pixels("000000000000000000000000000000000000000000000000000000000000000000000000000") #should be resolution independent? 825px on 1080p 1x scaling
        h = g.measure_in_pixels("0000000000000000000000000000000000000") #407px on 1080p 1x scaling
        self.minsize(w, h)

        icon = tk.PhotoImage(file=os.path.join(self.in_exe_path, "data", "icon.png"))
        self.wm_iconphoto(True, icon)

        mf = MainFrame(self)
        mf.grid(column=0, row=0, sticky=("N", "S", "E", "W"))

    #https://stackoverflow.com/a/70724666
    def set_titlebar_color(self, value):
        self.update()
        hwnd = windll.user32.GetParent(self.winfo_id())
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1 = 19
        if windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, byref(c_int(value)), sizeof(c_int(value))) != 0:
            windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1, byref(c_int(value)), sizeof(c_int(value)))

        #title bar needs to change ever so slightly, doesnt update otherwise :(
        if self.state() == "zoomed":
            self.state('normal')
            self.state('zoomed')
        else:
            self.attributes("-alpha", 0.99)
            self.attributes("-alpha", 1)


if __name__ == "__main__":
    g.root = MainWindow()
    g.root.mainloop()