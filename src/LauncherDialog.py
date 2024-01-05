import tkinter as tk 
from tkinter import ttk
import Globals as g

class LauncherDialog(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        self.frame = ttk.Frame(self, style='Card.TFrame', padding=(6, 6, 7, 7))
        self.frame.grid(column=0, row=0, sticky=("NEWS"), padx=(5,5), pady=(7,7))
        
        ttk.Label(self.frame, text="Enter launcher name:").grid(row=0, column=0, sticky=("N", "W"), padx=(3,0), pady=(0,5))
        
        self.launcher_name = tk.StringVar()
        self.entry = ttk.Entry(self.frame, width = 20, textvariable=self.launcher_name)
        self.entry.grid(column=0, row = 1, sticky=("W", "S"), padx=(3, 7))
        
        self.done_button = ttk.Button(self.frame, text = "Done", command = self.on_button)
        self.done_button.grid(column=1, row=1, sticky=("S", "E"), padx=(0, 7))

        self.cancel_button = ttk.Button(self.frame, text = "Cancel", command = self.on_cancel_button)
        self.cancel_button.grid(column=2, row=1, sticky=("S", "E"), padx=(0, 0))
        
        self.entry.bind("<Return>", self.on_button)
        self.launcher_name.trace_add("write", self.on_entry)
        self.done_button.config(state="disabled")

        rx = g.root.winfo_x()
        ry = g.root.winfo_y()
        rw = g.root.winfo_width()
        rh = g.root.winfo_height()
        x = int(rx + 0.4 * rw)
        y = int(ry + 0.4 * rh)
        self.geometry(f"+{x}+{y}")

    def on_button(self, event=None):
        self.destroy()

    def on_cancel_button(self, event=None):
        self.launcher_name.set("")
        self.destroy()

    def show(self):
        self.wm_deiconify()
        #self.wait_visibility()
        self.grab_set()
        self.wait_window()
        return self.launcher_name.get()
    
    def on_entry(self, var, index, mode):
        if len(self.launcher_name.get()) == 0:
            self.done_button.config(state="disabled")
        else:
            self.done_button.config(state="normal")