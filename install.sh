#!/bin/bash
chmod +x /data/plugins/user_interface/audiotop/PeppyMeter/peppymeter.py
chmod +x /data/plugins/user_interface/audiotop/audiotop.py


echo "Install python dependencies"

sudo apt-get -y install python3-pip
sudo apt-get -y install python3-pygame
python3 -m pip install -r requirements.txt
sudo tar -xzf depends/PIL.tar.gz  -C /usr/local/lib/python3.7/dist-packages

echo "plugininstalled"