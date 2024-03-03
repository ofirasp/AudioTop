# General
* Audiotop is a volumio plugin which integrates volumio and peppymeter
 * The project code is based on peppymeter
   * https://github.com/project-owner/PeppyMeter
 * Using the peppyalsa driver
   * https://github.com/project-owner/peppyalsa
 * Runs on volumio os
   * https://volumio.com/get-started/
 * With raspberry pi 5


# version 1.0.0
## 3.3.2024
* Add new 3 types of meters using the volumio titles metadata 
  * In this version only support the 1280*400 resolution
  * "matablue" Blue 2Ch Circular
  * "metabar" 2Ch with linear bars
  * "metapioneercassete" 2Ch vertical linear  bars with  cassete animation

#  Installation
## Install volumio
* Install the lateset version of Volumio
* Browse to http://volumio.local/dev and enable ssh
## Install peppyalsa
* ssh volumio@volumio.local
* git clone https://github.com/project-owner/peppyalsa.git
* sudo apt-get install build-essential autoconf automake libtool libasound2-dev libfftw3-dev
* cd peppyalsa
* aclocal && libtoolize
* autoconf && automake --add-missing
* ./configure && make
* sudo make install
* mkfifo /home/volumio/myfifo
* chmod 777 /home/volumio/myfifo
## install Audiotop plugin
*  git clone https://github.com/ofirasp/AudioTop.git
* 

