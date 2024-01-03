#add launchers
#get folder paths for launchers
#view games for each folder
#recognize junctions and match them
#GUI

import json
import os


class Launcher(object):
    def __init__(self, name):
        self.name = name
        self.libraryFolders = []
        self.index = -1
        #match name to icon?
    
    def add_library_folder(self, path):
        if not path in self.libraryFolders:
            self.libraryFolders.append(LibraryFolder(path))
            self.libraryFolders.sort()

class LibraryFolder(object):
    def __init__(self, path):
        self.path = path
        self.games = []
        self.get_games()

    def __lt__(self, other):
        return self.path < other.path

    def get_games(self):
        gamesBak = self.games
        try:
            self.games = []
            for item in os.scandir(self.path):
                if item.is_dir():
                    full_dir = os.path.join(self.path, item.name)
                    if is_junction(full_dir):
                        self.games.append(GameFolder(item.name, self.path, 0, True, os.path.realpath(full_dir)))
                    else:
                        self.games.append(GameFolder(item.name, self.path, self.folder_size(full_dir)))    
        except OSError:
            print("error getting games, wrong path?")
            self.games = gamesBak

    #https://stackoverflow.com/questions/1392413/calculating-a-directorys-size-using-python
    def folder_size(self, path):
        total = 0
        for entry in os.scandir(path):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += self.folder_size(entry.path)
        return total


class GameFolder(object):
    def __init__(self, name, library, sizeInBytes = 0, isJunction = False, junctionTarget = None):
        self.name = name
        self.library = library
        self.sizeInBytes = sizeInBytes
        self.size = self.get_readable_size()
        self.isJunction = isJunction
        self.junctionTarget = junctionTarget
        self.isJunctionTarget = False
        self.originalPath = None

    def get_readable_size(self):
        if self.sizeInBytes > 1073741824:
            return "{:0.2f} GB".format(self.sizeInBytes / 1024 / 1024 / 1024)
        elif self.sizeInBytes > 1048576:
            return "{:0.2f} MB".format(self.sizeInBytes / 1024 / 1024)
        elif self.sizeInBytes > 1024:
            return "{:0.2f} KB".format(self.sizeInBytes / 1024)
        else:
            return str(self.sizeInBytes) + " B"


    

def is_junction(path):
    try:
        return bool(os.readlink(path))
    except OSError:
        return False

if __name__ == "__main__":
    steam1 = Launcher("steam")
    steam1.add_library_folder("S:\Steam\steamapps\common")
    steam1.add_library_folder("T:\Steam\steamapps\common")
    for game in steam1.libraryFolders[0].games:
        if game.isjunction:
            print(game.name + " --> " + game.junctionTarget)
        else:
            print(game.name)
    for x in steam1.libraryFolders:
        print(x.path)

