# General
* Audiotop is a volumio plugin which integrates volumio and peppymeter
 * The project code is based on peppymeter and peppyspectrum ("Picasso Edition" 2024.02.10) 
   * https://github.com/project-owner/PeppyMeter
   * https://github.com/project-owner/PeppySpectrum
 * Using the peppyalsa driver
   * https://github.com/project-owner/peppyalsa
 * Runs on volumio os (base version 3.631)
   * https://volumio.com/get-started/
 * With raspberry pi 5
 * Display - waveshare hdmi 7.9" 1280*400

# version 2.0.0
## 17.4.2024
* Add peppy spectrum analyzer support
  * "metabarspectrum" new meter with spectrum
 ![alt text](samples/s4.png)
* Add some settings to the volumio plugin to configue the meters switching method 

# version 1.0.0
## 3.3.2024
* Add new 3 types of meters using the volumio titles metadata 
  * With this version, only support the 1280*400 resolution
  * Custom skins can be added (for all resultion) 
    * Look at the meters.txt file
  * "matablue" Blue 2Ch Circular
 ![alt text](samples/s1.png)
  * "metabar" 2Ch with linear bars
 ![alt text](samples/s2.png)
  * "metapioneercassete" 2Ch vertical linear  bars with  cassete animation
 ![alt text](samples/s3.png)

#  Installation
## Install volumio
* Install the lateset version of Volumio
* Browse to http://volumio.local/dev and enable ssh
## Install peppyalsa
* ssh volumio@volumio.local 

    (password:volumio)

* git clone https://github.com/project-owner/peppyalsa.git
* sudo apt-get install build-essential autoconf automake libtool libasound2-dev libfftw3-dev
* cd peppyalsa
* aclocal && libtoolize
* autoconf && automake --add-missing
* ./configure && make
* sudo make install
* mkfifo /home/volumio/myfifo
* chmod 777 /home/volumio/myfifo
* mkfifo /home/volumio/myfifosa
* chmod 777 /home/volumio/myfifosa
## Install Audiotop plugin
* cd /home/volumio
* git clone https://github.com/ofirasp/AudioTop.git
* cd Audiotop
* volumio plugin install
## Install Touch Display plugin

* Install from the volumio UI
* Set the orientation to 270
## Fix orientation for waveshare 1280X400 display

mkdir /home/volumio/.config/openbox

cat >> /home/volumio/.config/openbox/autostart <<EOL

xrandr --output HDMI-1 --rotate left

EOL
* more info :https://www.waveshare.com/wiki/7.9inch_HDMI_LCD

