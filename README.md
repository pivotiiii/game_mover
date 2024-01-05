# Game Mover <img src="https://github.com/pivotiiii/game_mover/assets/17112987/622e3c95-d03c-4a48-ac15-9db0df8add67" width="25" height="25">

![github](https://github.com/pivotiiii/game_mover/assets/17112987/44abc4e1-f3fd-4167-b24f-5bbdf3da36fa)

Game Mover is a program that allows you to move games between launcher libraries that are saved on different drives without breaking anything (hopefully 🙃).

# Usage

WARNING: If you want to move games that are installed inside `C:\Program Files` or `C:\Program Files (x86)` you need to launch Game Mover as admin.

After opening Game Mover first add a launcher (just the name), then add the folders that contain the games.
You can add multiple launchers with multiple library folders.
Moving a game can be done by selecting a game and pressing the "Move it" button below the folder you want to move it to.
Moving a game creates a directory junction that points to the new location.
Games that have been moved are marked with a small graphic that displays where they have been moved to.
Returning a game to its original location can be done the same way.

Game Mover can also be used to just manage junctions in general, not just games.

# Notice

Game Mover uses the [Sun Valley theme for ttk](https://github.com/rdbende/Sun-Valley-ttk-theme) by [rdbende](https://github.com/rdbende).
