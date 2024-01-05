import tkinter as tk 
from tkinter import ttk
import os
import subprocess
import _winapi
import Globals as g

class LibViewFrame(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.config(style='Card.TFrame', padding=(6, 6, 7, 7))
        if g.debug: self.config(bg = "blue")
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
            lfs = g.config.selected_launcher.libraryFolders
        except (KeyError, IndexError, AttributeError):
            lfs = []
        if g.debug: print("libdirs for " + g.config.selected_launcher.name + " are " + str([folder.path for folder in lfs]))
        
        if g.debug: print(self.winfo_width())
        self.destroy_widgets()

        #self.master.launcher_frame.grid_configure(column=len(self.library_dirs), row=0, sticky=)

        for i in range(0, len(lfs)):
            j = (i + 1) * 3 - 2

            self.labels.append(ttk.Label(self, text=lfs[i].path))
            self.labels[-1].grid(column=j, row=0, sticky=("W"), padx=5, pady=(0, 5))

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
            self.scrollbars[-1].grid(column=j+2, row=1, sticky=("N", "S", "W"), padx=(0, 5))
            self.trees[-1]["yscrollcommand"] = self.scrollbars[-1].set

            self.move_buttons.append(ttk.Button(self, text="Move here"))
            self.move_buttons[-1].config(state="disabled", command=lambda button=self.move_buttons[-1]: self.on_move_button(button))
            self.move_buttons[-1].grid(column=j, row=2, sticky=("W", "E"), padx=(3, 5), pady=(5, 0))

            self.del_buttons.append(ttk.Button(self, text="X", width=2))
            self.del_buttons[-1].config(command=lambda button=self.del_buttons[-1]: self.on_del_button(button))
            self.del_buttons[-1].grid(column=j+1, row=2, sticky=("E"), padx=(0, 0), pady=(5, 0))

            self.columnconfigure([j], minsize=300, weight=1)
            self.columnconfigure([j+1], minsize=10, weight=0)
        if len(self.scrollbars) > 0: self.scrollbars[-1].grid_configure(padx=0)
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
            if g.debug: print("selected heading")
            return
        selected_path = g.config.selected_launcher.libraryFolders[tree_id].path
        if g.debug: print(f"selected {selected_item} from tree {tree_id} with path {selected_path}")   

        for i in range(0, len(self.trees)):
            if i == tree_id: continue
            self.trees[i].selection_set([])
            
        g.config.set_selected_libraryFolder_by_index(tree_id)
        g.config.set_selected_game_by_string(selected_item)          

        if g.config.selected_game.isJunction:
            for button in self.move_buttons:
                button.config(state="disabled")
                button.config(text="Move here")
                button.config(style="TButton")
            self.move_buttons[tree_id].config(state="normal")
            self.move_buttons[tree_id].config(text="Return here")
            self.move_buttons[tree_id].config(style="Accent.TButton")
        else:
            for button in self.move_buttons:
                button.config(state="normal")
                button.config(text="Move here")
                button.config(style="TButton")
            self.move_buttons[tree_id].config(state="disabled")
        if g.config.selected_game.isJunctionTarget:
            lf = g.config.get_library_folder_by_path(g.config.selected_game.originalPath)
            index = g.config.get_library_folder_index_by_library_folder(lf)
            self.move_buttons[index].config(text="Return here")
            self.move_buttons[index].config(style="Accent.TButton")

    def on_del_button(self, button, event=None):
        buttonindex = int((button.grid_info()["column"]+1)/3-1)
        if g.debug: print("deleting libdir " + g.config.selected_launcher.libraryFolders[buttonindex].path)
        g.config.selected_launcher.libraryFolders.pop(buttonindex)
        self.master.recreate_libview_frame()
        g.config.save()

    def on_move_button(self, button, event=None):
        buttonindex = int((button.grid_info()["column"]+2)/3-1)
        game = g.config.selected_game
        if game.isJunction:
            #delete link, copy back to og path
            from_path = os.path.abspath(game.junctionTarget)
            to_path = os.path.abspath(os.path.join(game.library, game.name))
            os.unlink(to_path)
        elif game.isJunctionTarget:
            from_path = os.path.abspath(os.path.join(game.library, game.name))
            to_path = os.path.abspath(os.path.join(g.config.selected_launcher.libraryFolders[buttonindex].path, game.name))
            os.unlink(game.originalPath)
        else:
            #copy to new path, create junction
            from_path = os.path.abspath(os.path.join(g.config.selected_libraryFolder.path, game.name))
            to_path = os.path.abspath(os.path.join(g.config.selected_launcher.libraryFolders[buttonindex].path, game.name))
        
        if g.debug: print(f"moving game {game.name} from {from_path} to {to_path}")
        self.master.disable_all_frames()
        self.move_folders(from_path, to_path)
        
        self.master.enable_launcher_frame()

        if not game.isJunction and not game.isJunctionTarget:
            _winapi.CreateJunction(to_path, from_path)
        elif game.isJunctionTarget and to_path != os.path.abspath(game.originalPath):
            _winapi.CreateJunction(to_path, os.path.abspath(game.originalPath))
            
        for libraryFolder in g.config.selected_launcher.libraryFolders:
            libraryFolder.get_games()
        g.config.mark_junction_targets()
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
            #if g.debug: print(f"status: {cur_val} / {max_val}")
            self.master.progress.config(value=cur_val)
            g.root.update()#_idletasks()

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