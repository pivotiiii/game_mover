import tkinter as tk
import os
import sys
from MainFrame import MainFrame
from Config import Config
import Globals as g

#TODO
#game folder in both zB steamworks shared
#optics
#disable remove button if junctionpair found

g.debug = True

if __name__ == "__main__":
    near_exe_path = os.path.dirname(os.path.abspath(sys.argv[0]))   #for files in the same folder as the .exe created by nuitka
    in_exe_path = os.path.dirname(os.path.abspath(__file__))        #for files that should be included in the .exe (e.g. the icon)
    config_json = os.path.join(near_exe_path, "game_mover.json")

    g.config = Config(config_json)

    g.root = tk.Tk()
    g.root.title("Game Mover")
    g.root.columnconfigure(0, weight=1)
    g.root.rowconfigure(0, weight=1)

    g.init_font()

    w = g.measure_in_pixels("000000000000000000000000000000000000000000000000000000000000000000000000000") #should be resolution independent? 825px on 1080p 1x scaling
    h = g.measure_in_pixels("0000000000000000000000000000000000000") #407px on 1080p 1x scaling
    g.root.minsize(w, h)

    icon = tk.PhotoImage(file=os.path.join(in_exe_path, "data", "icon.png"))
    g.root.wm_iconphoto(True, icon)

    mf = MainFrame(g.root)
    mf.grid(column=0, row=0, sticky=("N", "S", "E", "W"))
    #if g.debug: mf.bind("<Configure>", g.widget_size_bind)

    g.root.mainloop()