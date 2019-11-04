# Monster Hunter World Database
<p align=center>
	<img src="images/mhw-title.png" alt="Title image">
</p>

This is a database program for Monster Hunter World.

It has been developed and tested on Windows. However since it's using wxPython it should be able to run on Linux and MacOS without too many modifications.

Most of the information is linked. Meaning you can double click on a list item to go to that item's page and load the information about it.

It contains the tabs with the following information:

* Monsters
* Weapons
* Armor
* Charms
* Decorations
* Skills
* Items
* Locations
  
In the near future I have plans to include a tab for kinsects as well. In addition to that I'm thinking of putting in the work to have a tab for quests and one for hunter tools(mantles/boosters).

<p align=center>
	<img src="images/screenshots.gif" alt="Screenshots GIF" width="800" height="500">
</p>

## Args

The project supports some command line arguments:

`-size` This sets the initial window size in pixels.

    -size <width> <height>
  
`-debug` Enables the the debug/log window on startup. This redirects all stdout, stderr and the wx errors to the debug window.

## Build

The only dependancy of the project is wxPython. (add python-ver , wx-ver)

## Credit

Thanks to @gatheringhallstudios for making the projects open source and with a permissive license.
Without their database I probably would never attempt to make this.
