#!/bin/bash

echo "Install Audiotop Dependencies"
echo "Executing sudo apt-get update"
sudo apt-get update
pluginpath=/data/plugins/user_interface/audiotop
peppyalsapath=/home/volumio/peppyalsa
peppypath=${pluginpath}/PeppyMeter


echo "Install python dependencies"
sudo apt-get -y install python3-pip
sudo apt-get -y install python3-pygame
pip3 install -r requirements.txt

########################################
# install peppyalsa
if [ ! -f "/usr/local/lib/libpeppyalsa.so" ]; then
        echo "Install peppyalsa"
        mkdir $peppyalsapath
        git clone https://github.com/project-owner/peppyalsa.git
        cd $peppyalsapath
        sudo apt-get -y install build-essential autoconf automake libtool libasound2-dev libfftw3-dev
        echo "___Compile peppyalsa..."
        aclocal && libtoolize
        autoconf && automake --add-missing
        ./configure && make
        sudo make install
else
    echo "peppyalsa already installed"
fi
mkfifo /home/volumio/myfifo
chmod 777 /home/volumio/myfifo

########################################
# build peppyalsa commandline client for test of installed peppyalsa
if [ -d "${$peppyalsapath}" ] && [ ! -f "${$peppyalsapath}/src/peppyalsa-client" ]; then
    echo "Compile peppyalsa-client"
    cd ${$peppyalsapath}/src
    if grep -q '/home/pi/myfifo' peppyalsa-client.c; then
        sudo sed -i 's/\/home\/pi\/myfifo/\/home\/volumio\/myfifo/g' peppyalsa-client.c
    fi
    sudo gcc peppyalsa-client.c -o peppyalsa-client
else
    echo "commandline tool already compiled"
fi
cdcdcdcdcdcdcd TODODODOD
# modify volumio alsa os file
sudo mv /volumio/app/plugins/audio_interface/alsa_controller/index.js /volumio/app/plugins/audio_interface/alsa_controller/index.js.original.js
sudo cp volumiomod/index.js.audiotop.js /volumio/app/plugins/audio_interface/alsa_controller/index.js


echo "If the plugin does not turn on after installing, restart Volumio"
echo "plugininstallend"