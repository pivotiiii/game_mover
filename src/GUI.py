import tkinter as tk
import os
import sys
from MainFrame import MainFrame
from Config import Config
import Globals as g

#TODO
#game folder in both zB steamworks shared
#cant move folder or parent of folder that is added

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


if __name__ == "__main__":
    g.root = MainWindow()
    g.root.mainloop()