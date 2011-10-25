### Minigame Test Launcher
## This file implements a minimal launcher which immediately allows you to
## launch into a specific minigame (via a commandline option), or see the
## usual minigame launcher, with a test user predefined, so that the tedious
## process of logging in and out can be avoided

import sys
import os
sys.path.insert(0, os.path.abspath("libraries"))

import games
import pygame
from optparse import OptionParser
import cProfile

import spyral

def format_columns(message, data, file = None):
    first_width = max([len(x[0]) for x in data])
    second_width = max([len(x[1]) for x in data])

    # calculate a format string for the output lines
    format_str= "%%-%ds        %%-%ds" % (first_width, second_width)

    if file is None:
        print message
        print "=" * (first_width + second_width + 8)
        for x in data:
            print format_str % x
    else:
        f = open(file, "w")
        format_str = format_str + "\n"
        f.write(message + "\n")
        f.write("=" * (first_width + second_width + 8) + "\n")
        for x in data:
            f.write(format_str % x)
        f.close()

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-g", "--game", dest="game", help="Choose the minigame to launch, defaults to showing a menu of selections.", metavar="GAME")
    parser.add_option("-l", "--list", action="store_true", dest="list", default=False, help="List available games and quit. To determine names for -g.")
    parser.add_option("-f", "--fullscreen", action="store_true", dest="fullscreen", default=False, help="Run in fullscreen mode. Default is windowed mode.")
    parser.add_option("-r", "--resolution", type="int", nargs=2, dest="res", help="Specify the resolution. Default is 0 0, which uses the screen's resolution.", metavar="WIDTH HEIGHT", default=(0,0))
    parser.add_option("-s", "--fps", type="int", dest="fps", help="Specify the fps cap. Default is 30", metavar="FPS", default=30)
    (options, args) = parser.parse_args()

    games = games.get_list()

    if options.list:
        for x in games:
            print "[" + x["short_name"] + "]" + "  " + x["name"]
        exit()
    
    if options.game is not None:
        launch = None
        for x in games:
            if x["short_name"] == options.game:
                launch = x["launch_func"]
                game_name = x["name"]
        if launch is None:
            print "Invalid minigame. Launch with -l to see a list of games."
            exit()
    else:
        x = -1
        while x not in range(len(games)):
            format_columns("Please choose a game", 
                [(str(i), x["name"]) for i,x in enumerate(games)])
            x = int(raw_input("\nMake your selection: "))
            print "\n"
        launch = games[x]["launch_func"]
            
        # Let's pull a game from the menu
        pass

    ## Let's output some friendly information at the top
    output = [
        ("resolution:", "Autodetect" if options.res == (0,0) else str(options.res[0]) + " x " + str(options.res[1])),
        ("fullscreen:", "True" if options.fullscreen else "False"),
        ("Max FPS:", str(options.fps)),
        ("game:", ("Menu" if options.game is None else game_name)),
        ]
    output.append(("switches: ", " ".join(sys.argv[1:])))
    format_columns("CISC374 Minigame Test Launcher Config", output)
            
    try:
        spyral.director.init(options.res, fullscreen = options.fullscreen, max_fps = options.fps)
        launch()
        spyral.director.run()
    except KeyboardInterrupt:
        pygame.quit()