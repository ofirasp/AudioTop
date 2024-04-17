#!/bin/bash
chmod +x /data/plugins/user_interface/audiotop/PeppyMeter/peppymeter.py
chmod +x /data/plugins/user_interface/audiotop/audiotop.py

# modify volumio alsa os file


#sudo mv /volumio/app/plugins/audio_interface/alsa_controller/index.js /volumio/app/plugins/audio_interface/alsa_controller/index.js.original.js
#sudo cp volumiomod/index.js.audiotop.js /volumio/app/plugins/audio_interface/alsa_controller/index.js


#echo "Install python dependencies"
#sudo apt-get update
#sudo apt-get -y install python3-pip
#sudo apt-get -y install python3-pygame
#python3 -m pip install -r requirements.txt
#sudo tar -xzf dependecies/PIL.tar.gz  -C /usr/local/lib/python3.7/dist-packages

echo "plugininstalled"