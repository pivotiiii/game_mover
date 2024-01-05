import tkinter as tk 
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import os
import game_mover
from LauncherDialog import LauncherDialog
import Globals as g

class LauncherFrame(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.config(style='Card.TFrame', padding=(6, 6, 7, 7))

        self.selected_launcher_cb = tk.StringVar()
        try:
            self.selected_launcher_cb.set(g.config.selected_launcher.name)
        except AttributeError:
            self.selected_launcher_cb.set("")

        self.selected_launcher_combobox = ttk.Combobox(self, textvariable=self.selected_launcher_cb)
        self.selected_launcher_combobox.state(["readonly"])
        self.selected_launcher_combobox.bind("<<ComboboxSelected>>", self.on_launcher_change)
        self.selected_launcher_combobox.grid(column=0, row=0, sticky=("N", "W", "S"))
        
    

        #self.selected_launcher_optionmenu = ttk.OptionMenu(self, variable=self.selected_launcher_cb, direction="below", command=self.on_launcher_change)
        #self.selected_launcher_optionmenu.grid(column=0, row=0, sticky=("nws"))

        self.add_launcher_button = ttk.Button(self, text="Add Launcher", command=self.on_add_launcher, width=15)
        if len(g.config.get_launcher_names()) == 0:
            self.add_launcher_button.configure(style="Accent.TButton")
        self.add_launcher_button.grid(column=1, row=0, sticky=("W"), padx=(5, 0))

        self.add_lib_button = ttk.Button(self, text="Add Folder", command=self.on_add_lib, width=15)
        if len(g.config.get_launcher_names()) > 0 and len(g.config.selected_launcher.libraryFolders) == 0:
            self.add_lib_button.configure(style="Accent.TButton")
        self.add_lib_button.grid(column=2, row=0, sticky=("W"), padx=(5, 0))


        self.remove_launcher_button = ttk.Button(self, text="Remove Launcher", command=self.on_remove_launcher, width=15)
        self.remove_launcher_button.grid(column=3, row=0, sticky=("W"), padx=(5, 0))



        self.refresh()

    def refresh(self):
        names = g.config.get_launcher_names()
        names.sort()
        if g.debug: print(f"launcher names: {names}")
        self.selected_launcher_combobox["values"] = names
        try:
            self.selected_launcher_combobox.set(g.config.selected_launcher.name)
        except AttributeError:
            self.selected_launcher_combobox.set("")

    def on_add_launcher(self, event=None):
        launcher_name = LauncherDialog(self).show()
        if launcher_name.lower() == "steam":
            mb = messagebox.askyesno("Added Steam", 
                                     "It seems like you want to add Steam.\n"
                                     "Steam has a built in function to move games.\n"
                                     "To access it go to Steam > Settings > Storage.\n"
                                     "Add anyway?")
            if not mb:
                return
        elif launcher_name == "" or launcher_name == None:
            return
        elif launcher_name in g.config.get_launcher_names():
            messagebox.showerror("Error", f"{launcher_name} already exists.")
            return
        

        g.config.launchers[launcher_name] = game_mover.Launcher(launcher_name)
        g.config.set_selected_launcher_by_name(launcher_name)
        self.selected_launcher_cb.set(launcher_name)
        self.add_launcher_button.configure(style="TButton")
        self.add_lib_button.configure(style="Accent.TButton")
        self.master.libview_frame.recreate()
        g.root.focus_set()
        self.refresh()
        g.config.save()

    def on_remove_launcher(self):
        g.config.remove_selected_launcher()
        names = g.config.get_launcher_names()
        if len(names) > 0:
            names.sort()
            new_selection = names[0]
            g.config.set_selected_launcher_by_name(new_selection)
            self.selected_launcher_cb.set(new_selection)
        else:
            self.selected_launcher_cb.set("")
        self.master.libview_frame.recreate()
        g.root.focus_set()
        self.refresh()
        g.config.save()

    def on_add_lib(self, event=None):
        folder = filedialog.askdirectory()
        if folder == "":
            return
        for libraryFolder in g.config.selected_launcher.libraryFolders:
            if os.path.abspath(folder) == os.path.abspath(libraryFolder.path):
                messagebox.showerror("Error", f"Folder already added.")
                return
        g.config.selected_launcher.add_library_folder(folder)
        self.add_lib_button.configure(style="TButton")
        self.master.libview_frame.refresh()
        g.root.focus_set()
        g.config.save()

    def on_launcher_change(self, event=None):
        name = self.selected_launcher_cb.get()
        g.config.set_selected_launcher_by_name(name)
        if len(g.config.selected_launcher.libraryFolders) == 0:
            self.add_lib_button.configure(style="Accent.TButton")
        else:
            self.add_lib_button.configure(style="TButton")
        if g.debug: print(f"switched to '{g.config.selected_launcher.name}'")
        self.master.libview_frame.recreate()
        self.selected_launcher_combobox.select_clear()
        g.root.focus_set()
        g.config.save()