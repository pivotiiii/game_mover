import tkinter as tk
import os
import sys
from MainFrame import MainFrame
from Config import Config
import Globals as g

#TODO
#game folder in both zB steamworks shared
#optics

g.debug = False

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
    #MainFrame(g.root).grid(column=0, row=0, sticky=("N", "S", "E", "W"))
    mf = MainFrame(g.root)
    #mf.pack(fill="both", expand=True)
    mf.grid(column=0, row=0, sticky=("N", "S", "E", "W"))
    #mf.bind("<Configure>", print_size)
    g.root.minsize(820, 405)
    icon = tk.PhotoImage(file=os.path.join(in_exe_path, "data", "icon.png"))
    g.root.wm_iconphoto(True, icon)
    print(f"'Remove Launcher' is {g.measure_in_pixels('Remove Launcher')} pixels and {g.measure_in_text_units('Remove Launcher')} text units wide")
    #g.root.update()
    #print(mf.launcher_frame.remove_launcher_button.winfo_reqwidth())
    g.root.mainloop()