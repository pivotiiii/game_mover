import tkinter as tk
from tkinter import ttk
import sv_ttk
from LauncherFrame import LauncherFrame
from LibViewFrame import LibViewFrame
import Globals as g

class MainFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.launcher_frame = LauncherFrame(self)
        self.launcher_frame.grid(column=0, row=0, sticky=("W"), padx=(5, 0), pady=(10, 0))

        self.libview_frame = LibViewFrame(self)
        self.libview_frame.grid(column=0, columnspan=3, row=1, sticky=("N", "W", "E", "S"), padx=(5, 5), pady=(10, 0))

        self.progress_frame = ttk.Frame(self)
        self.progress_frame.config(style='Card.TFrame', padding=(6, 6, 7, 7))
        self.progress_frame.grid(column=0, columnspan=3, row=2, sticky=("W", "E"), padx=(5, 5), pady=(10, 5))
        self.progress_frame.columnconfigure(0, weight=1)
        self.progress = ttk.Progressbar(self.progress_frame, orient="horizontal", mode="determinate")
        self.progress.grid(column=0, row=0, sticky=("W", "E"))
        #self.progress.grid(column=0, columnspan=3, row=2, sticky=("W", "E"))

        self.is_dark_mode = tk.BooleanVar() #read from config
        self.is_dark_mode.set(g.config.is_dark_mode)
        self.theme_label = ttk.Label(self, text="Dark Mode")
        self.theme_label.grid(column=1, row=0, sticky=("E"), pady=(10, 0))
        self.theme_switch = ttk.Checkbutton(self, style="Switch.TCheckbutton", variable=self.is_dark_mode, command=self.set_theme)
        self.theme_switch.grid(column=2, row=0, sticky=("E"), pady=(10, 0))
        try:
            self.set_theme()
        except AttributeError:
            pass

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight = 0)
        self.rowconfigure(1, weight = 1)

    def set_theme(self):
        if self.is_dark_mode.get():
            sv_ttk.set_theme("dark")
            g.config.is_dark_mode = True
        else:
            sv_ttk.set_theme("light")
            g.config.is_dark_mode = False
        g.config.save()
            
    def disable_all_frames(self):
        for frame in [self.launcher_frame, self.libview_frame]:
            for child in frame.winfo_children():
                wtype = child.winfo_class()
                if wtype in ("Frame", "Labelframe", "TFrame", "TLabelframe"):
                    continue
                    #self.enable_children(child, enabled)
                elif wtype in ["Treeview"]:
                    child.state((tk.DISABLED, ))
                    child.bind("<Button-1>", lambda e: "break")
                    child.bind("<ButtonRelease-1>", lambda event: "break")
                elif wtype in ["TScrollbar"]:
                    continue
                else:
                    child.config(state = tk.DISABLED)

    def enable_launcher_frame(self):
        for child in self.launcher_frame.winfo_children():
            child.config(state=tk.NORMAL)

    def recreate_libview_frame(self):
        self.libview_frame.destroy()
        self.libview_frame = LibViewFrame(self)
        self.libview_frame.grid(column=0, columnspan=3, row=1, sticky=("N", "W", "E", "S"), padx=(5, 5), pady=(10, 0))