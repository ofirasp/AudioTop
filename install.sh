#!/bin/bash

echo "Install Audiotop Dependencies"
echo "    Executing sudo apt-get update"
sudo apt-get update
plugin_path=/data/plugins/user_interface/PeppyMeter

echo "Install python dependencies"
sudo apt-get -y install python3-pip
sudo apt-get -y install python3-pygame


echo "If the plugin does not turn on after installing, restart Volumio"
echo "plugininstallend"
j5bv