"""
Using this file, you can quickly customize the GUI to sort as many categories as needed

Core buttons should not be added or deleted, but can be remapped to new keys
(ie change unsort from "0" to "U" to unsort with the U Key)

folders_to_sort is where you can add new categories as dictionary items-
just add "folder_name":"keybinding" to the dictionary.
(make sure to throw a comma in the line above your new entry)

Tip: Use capital letters, and special keys (shift, enter, etc) are not recommended
"""

unsorted_path = "/Users/thomasunderwood/Desktop/GitHub/videosorter/unsorted"

# Remap but DO NOT ADD/DELETE
core_buttons = {
    "play_pause": "Space",
    "restart": "R",
    "unsort": "0"
}

# Add sorting folders, and remap current ones
folders_to_sort = {
    "major_seizure": "1",
    "minor_seizure": "2",
    "night_nonseizure": "3",
    "day_nonsleeping": "4",
    "exclude": "9"
}



