#!/bin/bash

# Stop any running scripts.
sudo killall python

# Optional: This plugin installed python-mpd and python-smbus. If you want to remove these while uninstalling the plugin, uncomment the line below.

#sudo apt-get remove python-mpd python-smbus

echo "Done"
# Tell Volumio to delete the plugin files now.
echo "pluginuninstallend"
