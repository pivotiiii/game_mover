import tkinter as tk 
from tkinter import ttk
from tkinter import filedialog 
from tkinter.scrolledtext import ScrolledText
import game_mover
import json
import os

config_json = "game_mover.json"
debug = True

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
            json.dump(self.config, file)
    
    def write_config_file(self, dic):
        with open(self.config_json, "w") as file:
            json.dump(self.config, file)

class MainFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.config = Config()
        self.launchers = self.config.launchers
        self.launcher_names = self.get_launcher_names()

        self.selected_launcher = tk.StringVar()
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

        self.refresh()

    def refresh(self):
        names = [launcher for launcher in self.master.launchers]
        names.sort()
        if debug: print(names)
        self.selected_launcher_combobox["values"] = names
        self.selected_launcher_combobox.set(self.master.selected_launcher.get())

    def on_add_launcher(self, event=None):
        launcher = LauncherDialog(self).show()
        self.master.launchers[launcher] = game_mover.Launcher(launcher)
        self.master.selected_launcher.set(launcher)
        self.master.save_config()
        self.refresh()

    def on_add_lib(self, event=None):
        #folder = FolderDialog(self).show()
        folder = filedialog.askdirectory()
        self.master.launchers[self.master.selected_launcher.get()].add_library_folder(folder)
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
        self.buttons = []
        self.del_buttons = []
        self.last_selected_tree_index = -1
        self.last_selected_value = ""
        self.refresh()
        
    def refresh(self):
        self.last_selected_tree_index = -1
        self.last_selected_value = ""
        
        try:
            self.library_dirs = self.master.launchers[self.master.selected_launcher.get()].libraryFolders
        except IndexError:
            self.library_dirs = []
        if debug: print("libdirs for " + self.master.selected_launcher.get() + " are " + str([folder.path for folder in self.library_dirs]))
        self.destroy_widgets()

        for i in range(0, len(self.library_dirs)):
            j = (i + 1) * 3 - 2
            self.labels.append(ttk.Label(self, text=self.library_dirs[i].path))
            self.labels[-1].grid(column=j, row=0, sticky=("S", "W", "E"), padx=5)

            self.del_buttons.append(ttk.Button(self, text="X", width=2))
            self.del_buttons[-1].config(command=lambda button=self.del_buttons[-1]: self.on_del_button(button))
            self.del_buttons[-1].grid(column=j+1, row=2, sticky=("N", "E"))
            
            self.trees.append(ttk.Treeview(self, columns=("size", "arrow")))
            self.trees[-1].column("size", width=100, anchor="e")
            self.trees[-1].heading("size", text="Size")
            self.trees[-1].column("arrow", width=100, anchor="center")

            #self.trees[-1].bind("<ButtonRelease-1>", self.on_selection)
            self.trees[-1].bind("<ButtonRelease-1>", lambda tree=self.trees[-1]: self.on_selection(tree))

            for game in self.library_dirs[i].games:
                self.trees[-1].insert("", "end", game.name, text=game.name, values=(game.size, str(game.isJunction)))
            self.trees[-1].grid(column=j, columnspan=2, row=1, sticky=("N", "W", "E", "S"), padx=(3, 0))
            
            self.scrollbars.append(ttk.Scrollbar(self, orient="vertical", command=self.trees[-1].yview))
            self.scrollbars[-1].grid(column=j+2, row=1, sticky=("N", "S"), padx=(0, 3))
            self.trees[-1]["yscrollcommand"] = self.scrollbars[-1].set

            self.buttons.append(ttk.Button(self, text="Move here"))
            self.buttons[-1].config(state="disabled", command=lambda button=self.buttons[-1]: self.on_move_button(button))
            self.buttons[-1].grid(column=j, row=2, sticky=("S", "W", "E"), padx=5)

            self.columnconfigure([j], minsize=300, weight=1)#, pady=50)
            self.columnconfigure([j+1], minsize=10, weight=0)#, pady=50)
            self.rowconfigure([0, 2], weight=0, minsize=10)
            self.rowconfigure([1], minsize=300, weight=1)

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
        for button in self.buttons:
            button.destroy()
        self.buttons = []
        for button in self.del_buttons:
            button.destroy()
        self.del_buttons = []
    
    def on_selection(self, selected_tree, event=None):
            selected_items = []
            i = 0
            for tree in self.trees:
                for item in tree.selection():
                    selected_items.append((item, i))
                tree.selection_set(())
                i = i + 1
            if self.last_selected_value == selected_items[0][0]:
                self.last_selected_value = selected_items[-1][0]
                self.last_selected_tree_index = selected_items[-1][1]
            else:
                self.last_selected_value = selected_items[0][0]
                self.last_selected_tree_index = selected_items[0][1]

            if debug: print("selected " + self.last_selected_value + " from tree " + str(self.last_selected_tree_index))    
            self.trees[self.last_selected_tree_index].selection_set((self.last_selected_value, ))
            #self.master.selected_game = [game for game in self.master.launchers[self.master.selected_launcher.get()].libraryFolders[self.last_selected_tree_index].games if game.name == self.last_selected_value][0]
            self.master.set_selected_libraryFolder_by_index(self.last_selected_tree_index)
            self.master.set_selected_game_by_string(self.last_selected_value)
            

            for button in self.buttons:
                button.config(state="normal")
            if self.master.selected_game.isJunction:
                for button in self.buttons:
                    button.config(state="disabled")
            self.buttons[self.last_selected_tree_index].config(state="disabled")

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