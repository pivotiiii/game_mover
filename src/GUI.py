import tkinter as tk 
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import game_mover
import json
import os
import subprocess
import _winapi
import sv_ttk

#TODO
#game folder in both zB steamworks shared
#remove launcher
#heading Game in tree
#always use json next to .py /.exe

config_json = "game_mover.json"
debug = False

class Config(object):
    def __init__(self):
        self.config_json = config_json
        self.config = self.read_config_file()

        try:
            self.is_dark_mode = self.config["dark_mode"]
        except KeyError:
            self.is_dark_mode = False

        self.launchers = self._setup_launchers()
        self.mark_junction_targets()
        
        if self.config["last_selected"] in self.get_launcher_names():
            self.selected_launcher = self.launchers[self.config["last_selected"]]
        else:
            self.selected_launcher = None

        self.selected_game = None
        self.selected_libraryFolder = None

    def read_config_file(self):
        try:
            with open(self.config_json, "r") as file:
                if debug: print("loaded json")
                return json.load(file)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            with open(config_json, "w") as file:
                d = dict()
                d["dark_mode"] = False
                d["last_selected"] = ""
                d["launchers"] = dict()
                json.dump(d, file)
                if debug: print("created json")
                return d

    def save(self, launcher_dict = None, last_selected = None):
        if not launcher_dict: launcher_dict = self.launchers
        if not last_selected: last_selected = self.selected_launcher.name
        config = dict()
        config["dark_mode"] = self.is_dark_mode
        config["last_selected"] = last_selected
        config["launchers"] = dict()
        for item in launcher_dict:
            config["launchers"][item] = dict()
            config["launchers"][item]["libraryFolders"] = []
            for folder in launcher_dict[item].libraryFolders:
                config["launchers"][item]["libraryFolders"].append(folder.path)
        with open(self.config_json, "w") as file:
            json.dump(config, file, indent=4)

    def _setup_launchers(self) -> dict:
        launchers = dict()
        for launcher in list(self.config["launchers"].keys()):
            launchers[launcher] = game_mover.Launcher(launcher)
        for launcher in launchers:
            for folder in self.config["launchers"][launcher]["libraryFolders"]:
                launchers[launcher].add_library_folder(folder)
        return launchers

    def get_launcher_names(self) -> list:
        return [launcher for launcher in self.launchers.keys()]
    
    def get_selected_launcher(self) -> game_mover.Launcher:
        return self.selected_launcher
    
    def set_selected_launcher_by_name(self, name) -> None:
        self.selected_launcher = self.launchers[name]
    
    def gsl(self) -> game_mover.Launcher:
        return self.selected_launcher
    
    def get_library_folder_by_path(self, path: str) -> game_mover.LibraryFolder:
        lfs = self.selected_launcher.libraryFolders
        for i in range(0, len(lfs)):
            try:
                if os.path.abspath(lfs[i].path) == os.path.commonpath([lfs[i].path, path]):
                    return lfs[i]
            except ValueError:
                continue
        return None
    
    def get_library_folder_index_by_library_folder(self, library_folder: game_mover.LibraryFolder) -> int:
        lfs = self.selected_launcher.libraryFolders
        return lfs.index(library_folder)
    
    def set_selected_libraryFolder_by_index(self, index: int) -> None:
        self.selected_libraryFolder = self.selected_launcher.libraryFolders[index]

    def set_selected_game_by_string(self, game_string: str) -> None:
        self.selected_game = [game for game in self.selected_libraryFolder.games if game.name == game_string][0]

    def set_game_as_junction_target(self, library_folder_index: int, game: game_mover.GameFolder) -> None:
        games = self.selected_launcher.libraryFolders[library_folder_index].games
        for i in range(0, len(games)):
            if games[i].name == game.name:
                self.selected_launcher.libraryFolders[library_folder_index].games[i].isJunctionTarget = True
                self.selected_launcher.libraryFolders[library_folder_index].games[i].originalPath = os.path.abspath(os.path.join(game.library, game.name))
                break

    def mark_junction_targets(self) -> None:
        for key, launcher in self.launchers.items():
            for library_folder in launcher.libraryFolders:
                for game in library_folder.games:
                    if game.isJunction:
                        for target_library_folder in launcher.libraryFolders:
                            try:
                                os.path.commonpath([target_library_folder.path, game.junctionTarget])
                            except ValueError:
                                continue
                            if os.path.abspath(target_library_folder.path) == os.path.commonpath([target_library_folder.path, game.junctionTarget]):
                                target_game_index = target_library_folder.game_names.index(game.name)
                                target_library_folder.games[target_game_index].isJunctionTarget = True
                                target_library_folder.games[target_game_index].originalPath = game.path
                                if debug: print(f"{game.name} original at {game.path} is actually at {target_library_folder.games[target_game_index]}")


class MainFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        if debug: self.config(bg = "red")

        self.launcher_frame = LauncherFrame(self)
        self.launcher_frame.grid(column=0, row=0, sticky=("W"), padx=5, pady=(10, 5))

        self.libview_frame = LibViewFrame(self)
        self.libview_frame.grid(column=0, columnspan=3, row=1, sticky=("N", "W", "E", "S"), pady=5)

        self.progress = ttk.Progressbar(self, orient="horizontal", mode="determinate")
        self.progress.grid(column=0, columnspan=3, row=2, sticky=("W", "E"))

        self.is_dark_mode = tk.BooleanVar() #read from config
        self.is_dark_mode.set(config.is_dark_mode)
        self.theme_label = ttk.Label(self, text="Dark Mode")
        self.theme_label.grid(column=1, row=0, sticky=("E"))
        self.theme_switch = ttk.Checkbutton(self, style="Switch.TCheckbutton", variable=self.is_dark_mode, command=self.set_theme)
        self.theme_switch.grid(column=2, row=0, sticky=("E"))
        self.set_theme()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight = 0)
        self.rowconfigure(1, weight = 1)

    def set_theme(self):
        if self.is_dark_mode.get():
            sv_ttk.set_theme("dark")
            config.is_dark_mode = True
        else:
            sv_ttk.set_theme("light")
            config.is_dark_mode = False
        config.save()
            
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


class LauncherFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        if debug: self.config(bg = "green")

        self.selected_launcher_cb = tk.StringVar()
        try:
            self.selected_launcher_cb.set(config.selected_launcher.name)
        except AttributeError:
            self.selected_launcher_cb.set("")

        self.selected_launcher_optionmenu = ttk.OptionMenu(self, variable=self.selected_launcher_cb, direction="below", command=self.on_launcher_change)
        self.selected_launcher_optionmenu.grid(column=0, row=0, sticky=("nws"))

        self.add_launcher_button = ttk.Button(self, text="Add Launcher", command=self.on_add_launcher)
        self.add_launcher_button.grid(column=1, row=0, sticky=("W"), padx=(2, 0))

        self.add_lib_button = ttk.Button(self, text="Add Folder", command=self.on_add_lib)
        self.add_lib_button.grid(column=2, row=0, sticky=("W"), padx=(2, 0))

        

        self.refresh()

    def refresh(self):
        names = config.get_launcher_names()
        names.sort()
        if debug: print(names)
        menu = self.selected_launcher_optionmenu["menu"]
        menu.delete(0, "end")
        for launcher_name in names:
            menu.add_command(label=launcher_name, command=lambda value=launcher_name: self.on_launcher_change(value))
        self.selected_launcher_optionmenu.config(width=-10)

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
        elif launcher_name in config.get_launcher_names():
            messagebox.showerror("Error", f"{launcher_name} already exists.")
            return
        

        config.launchers[launcher_name] = game_mover.Launcher(launcher_name)
        config.set_selected_launcher_by_name(launcher_name)
        self.selected_launcher_cb.set(launcher_name)
        self.master.libview_frame.recreate()
        self.refresh()
        config.save()

    def on_add_lib(self, event=None):
        folder = filedialog.askdirectory()
        for libraryFolder in config.selected_launcher.libraryFolders:
            if os.path.abspath(folder) == os.path.abspath(libraryFolder.path):
                messagebox.showerror("Error", f"Folder already added.")
                return
        config.selected_launcher.add_library_folder(folder)
        self.master.libview_frame.refresh()
        config.save()

    def on_launcher_change(self, name, event=None):
        config.set_selected_launcher_by_name(name)
        self.selected_launcher_cb.set(name)
        if debug: print("switched to " + config.selected_launcher)
        self.master.libview_frame.recreate()
        self.master.focus_set()
        config.save()
        


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
        try:#necessary?
            lfs = config.selected_launcher.libraryFolders
        except (KeyError, IndexError, AttributeError):
            lfs = []
        if debug: print("libdirs for " + config.selected_launcher.name + " are " + str([folder.path for folder in lfs]))
        
        if debug: print(self.winfo_width())
        self.destroy_widgets()

        #self.master.launcher_frame.grid_configure(column=len(self.library_dirs), row=0, sticky=)

        for i in range(0, len(lfs)):
            j = (i + 1) * 3 - 2

            self.labels.append(ttk.Label(self, text=lfs[i].path))
            self.labels[-1].grid(column=j, row=0, sticky=("W"), padx=5)

            self.trees.append(ttk.Treeview(self, selectmode="browse", columns=("size", "arrow")))
            self.trees[-1].heading('#0', text="Game")
            self.trees[-1].column("size", width=100, anchor="e")
            self.trees[-1].heading("size", text="Size")
            self.trees[-1].column("arrow", width=100, anchor="center")
            self.trees[-1].heading("arrow", text="Status")
            self.trees[-1].bind("<ButtonRelease-1>", lambda event, tree_id=i: self.on_selection(tree_id))

            for game in lfs[i].games:
                location_string = ""
                if game.isJunction:
                    location_string = str(game.junctionTarget)
                    for k in range(0, len(lfs)):
                        try:
                            if os.path.abspath(lfs[k].path) == os.path.commonpath([lfs[k].path, game.junctionTarget]):
                                location_string = self.build_location_string(i, k, len(lfs))
                        except ValueError:
                            continue
                elif game.isJunctionTarget:
                    location_string = "JUNCTION"
                self.trees[-1].insert("", "end", game.name, text=game.name, values=(game.size, location_string))

            self.trees[-1].grid(column=j, columnspan=2, row=1, sticky=("N", "W", "E", "S"), padx=(3, 0))
            
            self.scrollbars.append(ttk.Scrollbar(self, orient="vertical", command=self.trees[-1].yview))
            self.scrollbars[-1].grid(column=j+2, row=1, sticky=("N", "S", "W"), padx=(0, 3))
            self.trees[-1]["yscrollcommand"] = self.scrollbars[-1].set

            self.move_buttons.append(ttk.Button(self, text="Move here"))
            self.move_buttons[-1].config(state="disabled", command=lambda button=self.move_buttons[-1]: self.on_move_button(button))
            self.move_buttons[-1].grid(column=j, row=2, sticky=("W", "E"), padx=5, pady=5)

            self.del_buttons.append(ttk.Button(self, text="X", width=2))
            self.del_buttons[-1].config(command=lambda button=self.del_buttons[-1]: self.on_del_button(button))
            self.del_buttons[-1].grid(column=j+1, row=2, sticky=("E"), padx=(0, 5), pady=5)

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
        try:
            selected_item = self.trees[tree_id].selection()[0]
        except IndexError:
            if debug: print("selected heading")
            return
        selected_path = config.selected_launcher.libraryFolders[tree_id].path
        if debug: print(f"selected {selected_item} from tree {tree_id} with path {selected_path}")   

        for i in range(0, len(self.trees)):
            if i == tree_id: continue
            self.trees[i].selection_set([])
            
        config.set_selected_libraryFolder_by_index(tree_id)
        config.set_selected_game_by_string(selected_item)          

        if config.selected_game.isJunction:
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
        if config.selected_game.isJunctionTarget:
            lf = config.get_library_folder_by_path(config.selected_game.originalPath)
            index = config.get_library_folder_index_by_library_folder(lf)
            self.move_buttons[index].config(text="Return here")

    def on_del_button(self, button, event=None):
        buttonindex = int((button.grid_info()["column"]+1)/3-1)
        if debug: print("deleting libdir " + config.selected_launcher.libraryFolders[buttonindex].path)
        config.selected_launcher.libraryFolders.pop(buttonindex)
        self.master.libview_frame.refresh()
        config.save()

    def on_move_button(self, button, event=None):
        buttonindex = int((button.grid_info()["column"]+2)/3-1)
        game = config.selected_game
        if game.isJunction:
            #delete link, copy back to og path
            from_path = os.path.abspath(game.junctionTarget)
            to_path = os.path.abspath(os.path.join(game.library, game.name))
            os.unlink(to_path)
        elif game.isJunctionTarget:
            from_path = os.path.abspath(os.path.join(game.library, game.name))
            to_path = os.path.abspath(os.path.join(config.selected_launcher.libraryFolders[buttonindex].path, game.name))
            os.unlink(game.originalPath)
        else:
            #copy to new path, create junction
            from_path = os.path.abspath(os.path.join(config.selected_libraryFolder.path, game.name))
            to_path = os.path.abspath(os.path.join(config.selected_launcher.libraryFolders[buttonindex].path, game.name))
        
        if debug: print(f"moving game {game.name} from {from_path} to {to_path}")
        self.master.disable_all_frames()
        self.move_folders(from_path, to_path)
        
        self.master.enable_launcher_frame()

        if not game.isJunction and not game.isJunctionTarget:
            _winapi.CreateJunction(to_path, from_path)
        elif game.isJunctionTarget and to_path != os.path.abspath(game.originalPath):
            _winapi.CreateJunction(to_path, os.path.abspath(game.originalPath))
            
        for libraryFolder in config.selected_launcher.libraryFolders:
            libraryFolder.get_games()
        config.mark_junction_targets()
        self.refresh()

    def move_folders(self, from_path, to_path):
        cur_val = 0
        self.master.progress.config(value=cur_val)
        files, folders = self.count_files_dirs(from_path)
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


if __name__ == "__main__":
    config = Config()
    root = tk.Tk()
    root.title("Game Mover")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    #MainFrame(root).grid(column=0, row=0, sticky=("N", "S", "E", "W"))
    MainFrame(root).pack(fill="both", expand=True)
    root.mainloop()