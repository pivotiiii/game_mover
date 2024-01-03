import tkinter as tk 
from tkinter import ttk
from tkinter import filedialog 
from tkinter.scrolledtext import ScrolledText
import game_mover
import json
import os

config_json = "game_mover.json"
debug = True

ucross = "\u2612"
ucross2 = "\u22a0"
uboxline = "\u229f"
ucheck = "\u2611"
ubox = "\u2610"
uboxdot = "\u26f6"
#uarrowleft = "\u2190"
uarrowleft = "\u21fd"
#uarrowright = "\u2192"
uarrowright = "\u21fe"

class Config(object):
    def __init__(self):
        self.config_json = config_json
        self.config = self.read_config_file()
        self.launchers = dict()

        for launcher in list(self.config["launchers"].keys()):
            self.launchers[launcher] = game_mover.Launcher(launcher)
        for launcher in self.launchers:
            for folder in self.config["launchers"][launcher]["libraryFolders"]:
                self.launchers[launcher].add_library_folder(folder)
        self.last_selected = self.config["last_selected"]

    def read_config_file(self):
        try:
            with open(self.config_json, "r") as file:
                if debug: print("loaded json")
                return json.load(file)
        except FileNotFoundError:
            with open(config_json, "w") as file:
                d = dict()
                d["last_selected"] = ""
                d["launchers"] = dict()
                json.dump(d, file)
                if debug: print("created json")
                return d

    
    def save(self, launcher_dict, last_selected):
        self.config["last_selected"] = last_selected
        self.config["launchers"] = dict()
        for item in launcher_dict:
            self.config["launchers"][item] = dict()
            self.config["launchers"][item]["libraryFolders"] = []
            for folder in launcher_dict[item].libraryFolders:
                self.config["launchers"][item]["libraryFolders"].append(folder.path)
        with open(self.config_json, "w") as file:
            json.dump(self.config, file, indent=4)

class MainFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.config = Config()
        self.launchers = self.config.launchers
        self.launcher_names = self.get_launcher_names()

        self.selected_launcher = tk.StringVar()
        if not self.config.last_selected in self.launcher_names:
            self.selected_launcher.set("")
        else:
            self.selected_launcher.set(self.config.last_selected)
        self.selected_game = None
        self.selected_libraryFolder = None

        self.launcher_frame = LauncherFrame(self)
        self.launcher_frame.grid(column=0, row=0, sticky=("N", "W"), padx=5, pady=10)

        self.libview_frame = LibViewFrame(self)
        self.libview_frame.grid(column=0, row=1, sticky=("N", "W", "E", "S"), pady=10)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight = 0)
        self.rowconfigure(1, weight = 1)

    def get_selected_launcher(self):
        return self.launchers[self.selected_launcher.get()]
    
    def get_selected_launcher_name(self):
        return self.selected_launcher.get()
    
    def get_launcher_names(self):
        return [launcher for launcher in self.launchers]
    
    def get_selected_launcher_libraryFolders(self):
        return self.launchers[self.get_selected_launcher_name()].libraryFolders

    
    def get_selected_libraryFolder_by_index(self, id):
        return self.get_selected_launcher_libraryFolders()[id]
    
    def set_selected_libraryFolder_by_index(self, id):
        self.selected_libraryFolder =  self.get_selected_launcher_libraryFolders()[id]
    
    def set_selected_game_by_string(self, game_string):
        self.selected_game = [game for game in self.selected_libraryFolder.games if game.name == game_string][0]
            
    def save_config(self):
        self.config.save(self.launchers, self.selected_launcher.get())

        pass
        
class LauncherFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        
        #self.selected_launcher = tk.StringVar()

        self.selected_launcher_combobox = ttk.Combobox(self, textvariable=self.master.selected_launcher)
        self.selected_launcher_combobox.state(["readonly"])
        self.selected_launcher_combobox.bind("<<ComboboxSelected>>", self.on_launcher_change)
        self.selected_launcher_combobox.grid(column=0, row=0, sticky=("N", "W", "S"))

        self.add_launcher_button = ttk.Button(self, text="Add Launcher", command=self.on_add_launcher)
        self.add_launcher_button.grid(column=1, row=0, sticky=("N", "W", "S"))

        self.add_lib_button = ttk.Button(self, text="Add Folder", command=self.on_add_lib)
        self.add_lib_button.grid(column=2, row=0, sticky=("N", "W", "S", "E"))

        ttk.Label(self, text=ucross + uarrowleft + uboxdot).grid(column=3, row=0)


        self.refresh()

    def refresh(self):
        names = self.master.get_launcher_names()
        names.sort()
        if debug: print(names)
        self.selected_launcher_combobox["values"] = names
        self.selected_launcher_combobox.set(self.master.get_selected_launcher_name())

    def on_add_launcher(self, event=None):
        launcher = LauncherDialog(self).show()
        self.master.launchers[launcher] = game_mover.Launcher(launcher)
        self.master.selected_launcher.set(launcher)
        self.master.libview_frame.refresh()
        self.master.save_config()
        self.refresh()

    def on_add_lib(self, event=None):
        #folder = FolderDialog(self).show()
        folder = filedialog.askdirectory()
        self.master.get_selected_launcher().add_library_folder(folder)
        self.master.libview_frame.refresh()
        self.master.save_config()

    def on_launcher_change(self, event=None):
        if debug: print("switched to " + self.master.selected_launcher.get())
        self.master.libview_frame.refresh()
        self.master.save_config()

class LibViewFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.labels = []
        self.trees = []
        self.scrollbars = []
        self.move_buttons = []
        self.del_buttons = []
        self.refresh()
        
    def refresh(self):
        try:
            self.library_dirs = self.master.get_selected_launcher_libraryFolders()
        except KeyError or IndexError:
            self.library_dirs = []
        if debug: print("libdirs for " + self.master.selected_launcher.get() + " are " + str([folder.path for folder in self.library_dirs]))
        
        self.destroy_widgets()

        for i in range(0, len(self.library_dirs)):
            j = (i + 1) * 3 - 2

            self.labels.append(ttk.Label(self, text=self.library_dirs[i].path))
            self.labels[-1].grid(column=j, row=0, sticky=("S", "W", "E"), padx=5)

            self.trees.append(ttk.Treeview(self, selectmode="browse", columns=("size", "arrow")))
            self.trees[-1].column("size", width=100, anchor="e")
            self.trees[-1].heading("size", text="Size")
            self.trees[-1].column("arrow", width=100, anchor="center")
            self.trees[-1].bind("<ButtonRelease-1>", lambda event, tree_id=i: self.on_selection(tree_id))

            for game in self.library_dirs[i].games:
                location_string = ""
                if game.isJunction:
                    location_string = str(game.junctionTarget)
                    for k in range(0, len(self.library_dirs)):
                        try:
                            if os.path.abspath(self.library_dirs[k].path) == os.path.commonpath([self.library_dirs[k].path, game.junctionTarget]):
                                location_string = self.build_location_string(i, k, len(self.library_dirs))
                                print(f"treffer des targets {game.name} in dir {k}: {self.library_dirs[k].path}")
                        except ValueError:
                            continue
                self.trees[-1].insert("", "end", game.name, text=game.name, values=(game.size, location_string))
                
            self.trees[-1].grid(column=j, columnspan=2, row=1, sticky=("N", "W", "E", "S"), padx=(3, 0))
            
            self.scrollbars.append(ttk.Scrollbar(self, orient="vertical", command=self.trees[-1].yview))
            self.scrollbars[-1].grid(column=j+2, row=1, sticky=("N", "S"), padx=(0, 3))
            self.trees[-1]["yscrollcommand"] = self.scrollbars[-1].set

            self.move_buttons.append(ttk.Button(self, text="Move here"))
            self.move_buttons[-1].config(state="disabled", command=lambda button=self.move_buttons[-1]: self.on_move_button(button))
            self.move_buttons[-1].grid(column=j, row=2, sticky=("S", "W", "E"), padx=5)

            self.del_buttons.append(ttk.Button(self, text="X", width=2))
            self.del_buttons[-1].config(command=lambda button=self.del_buttons[-1]: self.on_del_button(button))
            self.del_buttons[-1].grid(column=j+1, row=2, sticky=("S", "E"))

            self.columnconfigure([j], minsize=300, weight=1)#, pady=50)
            self.columnconfigure([j+1], minsize=10, weight=0)#, pady=50)
            self.rowconfigure([0, 2], weight=0, minsize=10)
            self.rowconfigure([1], minsize=110, weight=1)

    def build_location_string(self, junctionId, targetId, length):
        location_string = " "
        arrow = " "
        junctionFound = False
        targetFound = False
        for i in range(0, length):
            if i == junctionId:
                location_string = location_string + " " + uboxdot + " "
                junctionFound = True
                if not targetFound:
                    arrow = uarrowright
            elif i == targetId:
                location_string = location_string + ucross
                targetFound = True
                if not junctionFound:
                    arrow = uarrowleft
            else:
                location_string = location_string + ubox
            if not i == length - 1:
                location_string = location_string + arrow
        return location_string

        
    
    def destroy_widgets(self):
        for tree in self.trees:
            tree.destroy()
        self.trees = []
        for label in self.labels:
            label.destroy()
        self.labels = []
        for scrollbar in self.scrollbars:
            scrollbar.destroy()
        self.scrollbars = []
        for button in self.move_buttons:
            button.destroy()
        self.move_buttons = []
        for button in self.del_buttons:
            button.destroy()
        self.del_buttons = []
    
    def on_selection(self, tree_id, event=None):
        selected_item = self.trees[tree_id].selection()[0]
        selected_path = self.library_dirs[tree_id].path
        if debug: print(f"selected {selected_item} from tree {tree_id} with path {selected_path}")    
        for i in range(0, len(self.trees)):
            if i == tree_id: continue
            self.trees[i].selection_set([])
            
        self.master.set_selected_libraryFolder_by_index(tree_id)
        self.master.set_selected_game_by_string(selected_item)            

        for button in self.move_buttons:
            button.config(state="normal")
        if self.master.selected_game.isJunction:
            for button in self.move_buttons:
                button.config(state="disabled")
        self.move_buttons[tree_id].config(state="disabled")

    def on_del_button(self, button, event=None):
        buttonindex = int((button.grid_info()["column"]+1)/3-1)
        if debug: print("deleting libdir " + self.master.launchers[self.master.selected_launcher.get()].libraryFolders[buttonindex].path)
        self.master.launchers[self.master.selected_launcher.get()].libraryFolders.pop(buttonindex)
        self.master.libview_frame.refresh()
        self.master.save_config()

    def on_move_button(self, button, event=None):
        buttonindex = int((button.grid_info()["column"]+2)/3-1)
        game = self.master.selected_game
        og_path = self.master.selected_libraryFolder.path
        alt_path = self.master.launchers[self.master.selected_launcher.get()].libraryFolders[buttonindex].path
        if debug: print(f"moving game {game.name} from {og_path} to {alt_path}")
        if debug: print(f"mklink /j {os.path.join(alt_path, game.name)} {os.path.join(og_path, game.name)}")
        #TODO


class LauncherDialog(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        ttk.Label(self, text="Launcher name:").grid(row=0, column=0, sticky=("N", "W", "E"))
        self.launcher_name = tk.StringVar()
        self.entry = ttk.Entry(self, width = 20, textvariable=self.launcher_name)
        self.entry.grid(column=0, row = 0, sticky=("N", "W", "E", "S"))
        ttk.Button(self, text = "Done", command = self.on_button).grid(column=1, row=0, sticky=("N", "S", "W"))
        self.entry.bind("<Return>", self.on_button)

    def on_button(self, event=None):
        self.destroy()

    def show(self):
        self.wm_deiconify()
        #self.wait_visibility()
        self.grab_set()
        self.wait_window()
        return self.launcher_name.get()

class FolderDialog(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        ttk.Label(self, text="Library Folder:").grid(row=0, column=0, sticky=("N", "W", "E"))
        self.lib_folder = tk.StringVar()
        self.entry = ttk.Entry(self, width = 40, textvariable=self.lib_folder, state="readonly")
        self.entry.grid(column=0, row = 0, sticky=("N", "W", "E", "S"))
        ttk.Button(self, text = "Select Folder", command = self.on_select_button).grid(column=1, row=0, sticky=("N", "S", "W"))
        ttk.Button(self, text = "Done", command = self.on_done_button).grid(column=2, row=0, sticky=("N", "S", "W"))
        #self.entry.bind("<Return>", self.on_done_button)

    def on_done_button(self, event=None):
        self.destroy()

    def on_select_button(self, event=None):
        self.lib_folder.set(filedialog.askdirectory())

    def show(self):
        self.wm_deiconify()
        #self.wait_visibility()
        self.grab_set()
        self.wait_window()
        return self.lib_folder.get()




if __name__ == "__main__":

    root = tk.Tk()
    root.title("Game Mover")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    #MainFrame(root).grid(column=0, row=0, sticky=("N", "S", "E", "W"))
    MainFrame(root).pack(fill="both", expand=True)
    root.mainloop()