import tkinter as tk 
from tkinter import ttk
import Globals as g

class LauncherDialog(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.transient(parent)
        
        ttk.Label(self, text="Enter launcher name:").grid(row=0, column=0, sticky=("N", "W", "E"))
        self.launcher_name = tk.StringVar()
        self.entry = ttk.Entry(self, width = 20, textvariable=self.launcher_name)
        self.entry.grid(column=0, row = 1, sticky=("W", "S"))
        ttk.Button(self, text = "Done", command = self.on_button).grid(column=1, row=1, sticky=("S", "E"))
        self.entry.bind("<Return>", self.on_button)

        rx = g.root.winfo_x()
        ry = g.root.winfo_y()
        rw = g.root.winfo_width()
        rh = g.root.winfo_height()
        x = int(rx + 0.4 * rw)
        y = int(ry + 0.4 * rh)
        self.geometry(f"+{x}+{y}")

    def on_button(self, event=None):
        self.destroy()

    def show(self):
        self.wm_deiconify()
        #self.wait_visibility()
        self.grab_set()
        self.wait_window()
        return self.launcher_name.get()