import json
import os
import game_mover
import Globals as g

class Config():
    def __init__(self, config_json):
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
                if g.debug: print("loaded json")
                return json.load(file)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            with open(self.config_json, "w") as file:
                d = dict()
                d["dark_mode"] = False
                d["last_selected"] = ""
                d["launchers"] = dict()
                json.dump(d, file)
                if g.debug: print("created json")
                return d

    def save(self, launcher_dict = None, last_selected = None):
        if self.selected_launcher == None:
            return
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

    def remove_selected_launcher(self) -> None:
        self.launchers.pop(self.selected_launcher.name)
        self.selected_launcher = None
    
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
                                if g.debug: print(f"{game.name} original at {game.path} is actually at {target_library_folder.games[target_game_index]}")