import tkinter as tk 
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import game_mover
import json
import os
import subprocess
import _winapi

#TODO
#game folder in both zB steamworks shared
#remove launcher
#modify bg treeview
#heading Game in tree
#toggle theme button
#always use json next to .py /.exe

config_json = "game_mover.json"
debug = False

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
        if debug: self.config(bg = "red")
        self.configObj = Config()
        self.launchers = self.configObj.launchers
        self.launcher_names = self.get_launcher_names()

        self.selected_launcher = tk.StringVar()
        if not self.configObj.last_selected in self.launcher_names:
            self.selected_launcher.set("")
        else:
            self.selected_launcher.set(self.configObj.last_selected)
        self.selected_game = None
        self.selected_libraryFolder = None

        
        

        self.launcher_frame = LauncherFrame(self)
        self.launcher_frame.grid(column=0, row=0, sticky=("W"), padx=5, pady=(10, 5))

        self.libview_frame = LibViewFrame(self)
        self.libview_frame.grid(column=0, columnspan=3, row=1, sticky=("N", "W", "E", "S"), pady=5)

        self.progress = ttk.Progressbar(self, orient="horizontal", mode="determinate")
        self.progress.grid(column=0, columnspan=3, row=2, sticky=("W", "E"))

        self.is_dark_theme = tk.BooleanVar() #read from config
        self.theme_label = ttk.Label(self, text="Dark Theme")
        self.theme_label.grid(column=1, row=0, sticky=("E"))
        self.theme_switch = ttk.Checkbutton(self, style="Switch.TCheckbutton", variable=self.is_dark_theme, command=self.set_theme)
        self.theme_switch.grid(column=2, row=0, sticky=("E"))

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight = 0)
        self.rowconfigure(1, weight = 1)

    def set_theme(self):
        if self.is_dark_theme.get():
            sv_ttk.set_theme("dark")
        else:
            sv_ttk.set_theme("light")

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
        self.libview_frame.grid(column=0, columnspan=3, row=1, sticky=("N", "W", "E", "S"), pady=5)
    
    def get_selected_launcher(self):
        return self.launchers[self.selected_launcher.get()]
    
    def get_selected_launcher_name(self):
        return self.selected_launcher.get()
    
    def get_launcher_names(self):
        return [launcher for launcher in self.launchers]
    
    def get_libraryFolder_by_path(self, path):
        lds = self.get_selected_launcher_libraryFolders()
        for i in range(0, len(lds)):
            try:
                if os.path.abspath(lds[i].path) == os.path.commonpath([lds[i].path, path]):
                    return lds[i]
            except ValueError:
                continue
        return None
    
    def get_selected_launcher_libraryFolders(self):
        return self.launchers[self.get_selected_launcher_name()].libraryFolders

    def get_selected_libraryFolder_by_index(self, id):
        return self.get_selected_launcher_libraryFolders()[id]
    
    def set_selected_libraryFolder_by_index(self, id):
        self.selected_libraryFolder = self.get_selected_launcher_libraryFolders()[id]
    
    def get_index_by_libraryFolder(self, libdir):
        ld = self.get_selected_launcher_libraryFolders()
        return ld.index(libdir)
    
    def set_selected_game_by_string(self, game_string):
        self.selected_game = [game for game in self.selected_libraryFolder.games if game.name == game_string][0]

    def set_game_as_junction_target(self, libraryFolderIndex, game):
        games = self.get_selected_launcher().libraryFolders[libraryFolderIndex].games
        for i in range(0, len(games)):
            if games[i].name == game.name:
                self.get_selected_launcher().libraryFolders[libraryFolderIndex].games[i].isJunctionTarget = True
                self.get_selected_launcher().libraryFolders[libraryFolderIndex].games[i].originalPath = os.path.abspath(os.path.join(game.library, game.name))
                break
            
    def save_config(self):
        self.configObj.save(self.launchers, self.selected_launcher.get())


class LauncherFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        if debug: self.config(bg = "green")

        #self.selected_launcher_combobox = ttk.Combobox(self, textvariable=self.master.selected_launcher)
        #self.selected_launcher_combobox.state(["readonly"])
        #self.selected_launcher_combobox.bind("<<ComboboxSelected>>", self.on_launcher_change)
        #self.selected_launcher_combobox.grid(column=0, row=0, sticky=("N", "W", "S"))
        self.selected_launcher_optionmenu = ttk.OptionMenu(self, variable=self.master.selected_launcher, direction="below", command=self.on_launcher_change)
        self.selected_launcher_optionmenu.grid(column=0, row=0, sticky=("nws"))

        self.add_launcher_button = ttk.Button(self, text="Add Launcher", command=self.on_add_launcher)
        self.add_launcher_button.grid(column=1, row=0, sticky=("W"), padx=(2, 0))

        self.add_lib_button = ttk.Button(self, text="Add Folder", command=self.on_add_lib)
        self.add_lib_button.grid(column=2, row=0, sticky=("W"), padx=(2, 0))

        

        self.refresh()

    def refresh(self):
        names = self.master.get_launcher_names()
        names.sort()
        if debug: print(names)
        #self.selected_launcher_combobox["values"] = names
        #self.selected_launcher_combobox.set(self.master.get_selected_launcher_name())
        #names = [""].append(names)
        menu = self.selected_launcher_optionmenu["menu"]
        menu.delete(0, "end")
        for launcher in names:
            menu.add_command(label=launcher, command=lambda value=launcher: self.on_launcher_change(value))
        
        self.selected_launcher_optionmenu.config(width=-10)
        #self.selected_launcher_optionmenu["values"] = names
        #self.selected_launcher_optionmenu.selection_own()

    def on_add_launcher(self, event=None):
        launcher = LauncherDialog(self).show()
        if launcher.lower() == "steam":
            mb = messagebox.askyesno("Added Steam", 
                                     "It seems like you want to add Steam.\n"
                                     "Steam has a built in function to move games.\n"
                                     "To access it go to Steam > Settings > Storage.\n"
                                     "Add anyway?")
            if not mb:
                return
        elif launcher == "" or launcher == None:
            return
        elif launcher in self.master.get_launcher_names():
            messagebox.showerror("Error", f"{launcher} already exists.")
            return
        

        self.master.launchers[launcher] = game_mover.Launcher(launcher)
        self.master.selected_launcher.set(launcher)
        self.master.libview_frame.recreate()
        self.master.save_config()
        self.refresh()

    def on_add_lib(self, event=None):
        #folder = FolderDialog(self).show()
        folder = filedialog.askdirectory()
        for libraryFolder in self.master.get_selected_launcher_libraryFolders():
            if os.path.abspath(folder) == os.path.abspath(libraryFolder.path):
                messagebox.showerror("Error", f"Folder already added.")
                return
        self.master.get_selected_launcher().add_library_folder(folder)
        self.master.libview_frame.refresh()
        self.master.save_config()

    def on_launcher_change(self, name, event=None):
        self.master.selected_launcher.set(name)
        if debug: print("switched to " + self.master.selected_launcher.get())
        self.master.libview_frame.recreate()
        self.master.focus_set()
        self.master.save_config()
        


class LibViewFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        if debug: self.config(bg = "blue")
        self.labels = []
        self.trees = []
        self.scrollbars = []
        self.move_buttons = []
        self.del_buttons = []
        self.refresh()
        
    def recreate(self):
        self.master.recreate_libview_frame()
    
    def refresh(self):
        try:
            self.library_dirs = self.master.get_selected_launcher_libraryFolders()
        except KeyError or IndexError:
            self.library_dirs = []
        if debug: print("libdirs for " + self.master.selected_launcher.get() + " are " + str([folder.path for folder in self.library_dirs]))
        
        if debug: print(self.winfo_width())
        self.destroy_widgets()

        #self.master.launcher_frame.grid_configure(column=len(self.library_dirs), row=0, sticky=)

        for i in range(0, len(self.library_dirs)):
            #first check all games to mark junction targets
            for game in self.library_dirs[i].games:
                location_string = ""
                if game.isJunction:
                    location_string = str(game.junctionTarget)
                    for k in range(0, len(self.library_dirs)):
                        try:
                            if os.path.abspath(self.library_dirs[k].path) == os.path.commonpath([self.library_dirs[k].path, game.junctionTarget]):
                                self.master.set_game_as_junction_target(k, game)
                        except ValueError:
                            continue

        for i in range(0, len(self.library_dirs)):
            j = (i + 1) * 3 - 2

            self.labels.append(ttk.Label(self, text=self.library_dirs[i].path))
            self.labels[-1].grid(column=j, row=0, sticky=("S", "W"), padx=5)

            self.trees.append(ttk.Treeview(self, selectmode="browse", columns=("size", "arrow")))
            self.trees[-1].column("size", width=100, anchor="e")
            self.trees[-1].heading("size", text="Size")
            self.trees[-1].column("arrow", width=100, anchor="center")
            self.trees[-1].bind("<ButtonRelease-1>", lambda event, tree_id=i: self.on_selection(tree_id))

            #second build location_strings that point to targets and mark targets as JUNCTION, then add to tree
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
                elif game.isJunctionTarget:
                    location_string = "JUNCTION"
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

            self.columnconfigure([j], minsize=300, weight=1)
            self.columnconfigure([j+1], minsize=10, weight=0)
        self.rowconfigure([0, 2], weight=0, minsize=10)
        self.rowconfigure([1], minsize=110, weight=1)

    def build_location_string(self, junctionId, targetId, length):
        ucross = "\u2612"
        ubox = "\u2610"
        uboxdot = "\u26f6"
        uarrowleft = "\u21fd"
        uarrowright = "\u21fe"

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
                elif targetFound and junctionFound:
                    arrow = " "
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

        if self.master.selected_game.isJunction:
            for button in self.move_buttons:
                button.config(state="disabled")
                button.config(text="Move here")
            self.move_buttons[tree_id].config(state="normal")
            self.move_buttons[tree_id].config(text="Return here")
        else:
            for button in self.move_buttons:
                button.config(state="normal")
                button.config(text="Move here")
            self.move_buttons[tree_id].config(state="disabled")
        if self.master.selected_game.isJunctionTarget:
            ld = self.master.get_libraryFolder_by_path(self.master.selected_game.originalPath)
            idx = self.master.get_index_by_libraryFolder(ld)
            self.move_buttons[idx].config(text="Return here")

    def on_del_button(self, button, event=None):
        buttonindex = int((button.grid_info()["column"]+1)/3-1)
        if debug: print("deleting libdir " + self.master.launchers[self.master.selected_launcher.get()].libraryFolders[buttonindex].path)
        self.master.launchers[self.master.selected_launcher.get()].libraryFolders.pop(buttonindex)
        self.master.libview_frame.refresh()
        self.master.save_config()

    def on_move_button(self, button, event=None):
        buttonindex = int((button.grid_info()["column"]+2)/3-1)
        game = self.master.selected_game
        if game.isJunction:
            #delete link, copy back to og path
            from_path = os.path.abspath(game.junctionTarget)
            to_path = os.path.abspath(os.path.join(game.library, game.name))
            os.unlink(to_path)
        elif game.isJunctionTarget:
            from_path = os.path.abspath(os.path.join(game.library, game.name))
            to_path = os.path.abspath(os.path.join(self.master.get_selected_launcher_libraryFolders()[buttonindex].path, game.name))
            os.unlink(game.originalPath)
        else:
            #copy to new path, create junction
            from_path = os.path.abspath(os.path.join(self.master.selected_libraryFolder.path, game.name))
            to_path = os.path.abspath(os.path.join(self.master.get_selected_launcher_libraryFolders()[buttonindex].path, game.name))
        
        if debug: print(f"moving game {game.name} from {from_path} to {to_path}")
        self.master.disable_all_frames()
        self.move_folders(from_path, to_path)
        self.master.enable_launcher_frame()

        if not game.isJunction and not game.isJunctionTarget:
            _winapi.CreateJunction(to_path, from_path)
        elif game.isJunctionTarget and to_path != os.path.abspath(game.originalPath):
            _winapi.CreateJunction(to_path, os.path.abspath(game.originalPath))
            
        for libraryFolder in self.master.get_selected_launcher_libraryFolders():
            libraryFolder.get_games()
        self.refresh()

    def move_folders(self, from_path, to_path):
        cur_val = 0
        self.master.progress.config(value=cur_val)
        files, folders = self.count_files_dirs(from_path) #vllt progress mit target folder size?
        max_val = files + folders + 2
        self.master.progress.config(maximum=max_val)

        p = subprocess.Popen(["robocopy", from_path, to_path, "/E", "/MOVE", "/NJH", "/NJS", "/NP"], stdout = subprocess.PIPE, bufsize=1, universal_newlines=True)
        while True:
            data = p.stdout.readline()
            if len(data) == 0: break
            cur_val = cur_val + 1
            #if debug: print(f"status: {cur_val} / {max_val}")
            self.master.progress.config(value=cur_val)
            root.update()#_idletasks()

    #https://stackoverflow.com/questions/16910330/return-total-number-of-files-in-directory-and-subdirectories
    def count_files_dirs(self, dir_path):
        folder_array = os.scandir(dir_path)
        files = 0
        folders = 0
        for path in folder_array:
            if path.is_file():
                files += 1
            elif path.is_dir():
                folders += 1
                file_count, folder_count = self.count_files_dirs(path)
                files += file_count
                folders += folder_count
        return files, folders

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

        rx = root.winfo_x()
        ry = root.winfo_y()
        rw = root.winfo_width()
        rh = root.winfo_height()
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
    mf = MainFrame(root)
    mf.pack(fill="both", expand=True)
    #if debug: mf.config(bg = "yellow")

    #root.tk.call("source", "src/themes/Forest-ttk-theme-1.0/forest-dark.tcl")
    #style = ttk.Style(root)
    #style.theme_use("forest-dark")

    #root.tk.call("source", "src/themes/Azure-ttk-theme-2.1.0/azure.tcl")
    #root.tk.call("set_theme", "dark")

    import sv_ttk
    sv_ttk.set_theme("dark")
        
    root.mainloop()