import pong

launcher_info = {
    # The name to be printed in the menu
    "name" : "Pong",
    # A shortname, to launch from the shell
    "short_name" : "pong",
    # A function which should launch the game
    "launch_func": pong.main,
    # The path to a preview image, 200x150px ideally.
    # Right now this is unused
    "preview" : "games/pong/images/preview.png"
    }