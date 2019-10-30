# Monster Hunter World Database

This is a database program for Monster Hunter World.

Most of the information is searchable and linked. Meaning you can double click on a list item to go to that item's page and load the information about it.

It contains pages with the following information:

* Monsters:
  * List of monsters small and large.
  * Summary of weaknesses, ailments and areas the monster moves between.
  * Hitzone information for physical and elemental damage as well as break/sever/kinsect extract information
  * Materials that come from the monster and under which conditions.
* Weapons:
  * Each weapon tree visualised with attack, affinity, defense, elderseal, sharpness info and more.
  * Includes Kulve Taroth weapons.
* Armor:
  * All armor pieces grouped by the armor set with defense values **for** inital, max and max augmented, elemental resistances, skills etc.

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
