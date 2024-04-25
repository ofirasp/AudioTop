# Copyright 2016-2024 PeppyMeter peppy.player@gmail.com
# 
# This file is part of PeppyMeter.
# 
# PeppyMeter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# PeppyMeter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with PeppyMeter. If not, see <http://www.gnu.org/licenses/>.
import logging
import sys
import time
import copy
import pygame
import socketio
import threading
from random import randrange
from meterfactory import MeterFactory
from screensavermeter import ScreensaverMeter
from configfileparser import METER, METER_NAMES, RANDOM_METER_INTERVAL, USE_CACHE, SCREEN_RECT, SCREEN_INFO, FRAME_RATE
NOSTATUS = -1
STOPPED = 0
STARTPLAYING = 2
PLAYING =3
STOPPING = 1
class Vumeter(ScreensaverMeter):

    """ VU Meter plug-in. """
    def on_message(self,data):
        self.metadata = data
        self.updatemetadata = True
        if self.metadata!=None and "title" in self.metadata:
            if self.currenttitle!=self.metadata['title']:
                self.currenttitle=self.metadata['title']
                self.titleupdate=True
        if self.metadata!=None and "album" in self.metadata:
            if self.currentalbum!=self.metadata['album']:
                self.currentalbum=self.metadata['album']
                self.albumupdate=True
        if self.metadata != None and "status" in self.metadata:

            if self.metadata['status'] == 'play':
                if self.playerstatus == STOPPED:
                    self.playerstatus = STARTPLAYING
                else:
                    self.playerstatus = PLAYING
            else:
                if self.playerstatus==PLAYING:
                    self.playerstatus=STOPPING
                else:
                    self.playerstatus=STOPPED




    def startsockio(self):
        try:
            self.sio.connect(f'http://{self.metadatasourcedns}:3000')
            self.sio.emit('getState', {})
            self.sio.wait()
        except Exception as ex:
            logging.error(ex)

    def diconnectsocketio(self):
        self.sio.disconnect()
    def __init__(self, util, data_source, timer_controlled_random_meter=True,autoswitchmeter=None,switchmeter=None):
        """ Initializer
        
        :param util: utility class
        """
        self.playerstatus=NOSTATUS
        self.metadata = {}
        self.autoswitchmeter = autoswitchmeter
        self.switchmeter = switchmeter
        self.updatemetadata = False
        self.titleupdate = False
        self.albumupdate = False
        self.currenttitle =''
        self.currentalbum = ''
        self.util = util
        self.update_period = 1
        self.meter = None
        self.meter_names = self.util.meter_config[METER_NAMES]
        self.metadatasourcedns = self.util.meter_config['metadatasourcedns']
        random_meter_interval = self.util.meter_config[RANDOM_METER_INTERVAL]
        frame_rate = self.util.meter_config[FRAME_RATE]
        self.frames_before_switch = random_meter_interval * frame_rate
        self.data_source = data_source
        self.timer_controlled_random_meter = timer_controlled_random_meter
        self.random_meter = False
        self.list_meter = False
        self.list_meter_index = 0
        
        if self.util.meter_config[METER] == "random":
            self.random_meter = True
            self.random_meter_names = copy.copy(self.meter_names)
        elif "," in self.util.meter_config[METER]:
            self.list_meter = True
            
        self.meter = None
        self.current_volume = 100.0
        self.frames = 0

        self.mono_needle_cache = {}
        self.mono_rect_cache = {}
        self.left_needle_cache = {}
        self.left_rect_cache = {}
        self.right_needle_cache = {}
        self.right_rect_cache = {}
        self.sio = socketio.Client()
        self.sio.on('pushState', self.on_message)
        x = threading.Thread(target=self.startsockio)
        x.start()
    
    def get_meter(self):
        """ Creates meter using meter factory. """  
              
        if self.meter and not (self.random_meter or self.list_meter):
            return self.meter
        
        if self.random_meter:
            if len(self.random_meter_names) == 0:
                self.random_meter_names = copy.copy(self.meter_names)
            i = randrange(0, len(self.random_meter_names))     
            self.util.meter_config[METER] = self.random_meter_names[i]
            del self.random_meter_names[i]
        elif self.list_meter:
            if self.list_meter_index == len(self.meter_names):
                self.list_meter_index = 0
            self.util.meter_config[METER] = self.meter_names[self.list_meter_index]
            self.list_meter_index += 1

        factory = MeterFactory(self.util, self.util.meter_config, self.data_source, self.mono_needle_cache, self.mono_rect_cache, self.left_needle_cache, self.left_rect_cache, self.right_needle_cache, self.right_rect_cache)
        m = factory.create_meter()

        return m
    def switchmeter1(self):
        self.list_meter_index = (self.list_meter_index + 1) % len(self.meterlist)
        self.util.meter_config[METER] = self.meterlist[self.list_meter_index]
        factory = MeterFactory(self.util, self.util.meter_config, self.data_source, self.mono_needle_cache,
                               self.mono_rect_cache, self.left_needle_cache, self.left_rect_cache,
                               self.right_needle_cache, self.right_rect_cache)
        self.meter = factory.create_meter()

    def set_volume(self, volume):
        """ Set volume level 

        :param volume: new volume level
        """

        self.current_volume = volume
    
    def start(self):
        """ Start data source and meter animation. """ 
               
        self.meter = self.get_meter()
        self.meter.set_volume(self.current_volume)
        self.meter.start()
        self.sio.emit('getState', {})
        if hasattr(self, "callback_start"):
            self.callback_start(self.meter)

    def run(self):
        """ Run meter  
        
        :return: list of rectangles for update
        """
        if self.meter:
            return self.meter.run()
        return None
    def pauseplayer(self):
        self.sio.emit('pause', '')
    def stop(self):
        """ Stop meter animation. """

        self.frames = 0
        self.meter.stop()
        self.sio.emit('getState', {})
        if hasattr(self, "callback_stop"):
            self.callback_stop(self.meter)

        if not self.util.meter_config[USE_CACHE]:
            del self.mono_needle_cache
            del self.mono_rect_cache
            del self.left_needle_cache
            del self.left_rect_cache
            del self.right_needle_cache
            del self.right_rect_cache
            del self.meter

            if hasattr(self, "malloc_trim"):
                self.malloc_trim()

            self.mono_needle_cache = {}
            self.mono_rect_cache = {}
            self.left_needle_cache = {}
            self.left_rect_cache = {}
            self.right_needle_cache = {}
            self.right_rect_cache = {}
            self.meter = None

    def restart(self):
        """ Restart random meter """

        self.stop()
        time.sleep(0.2) # let threads stop
        self.start()
        pygame.display.update(self.util.meter_config[SCREEN_RECT])
    
    def refresh(self):
        """ Refresh meter. Used to update random meter. """

        if(self.frames%self.util.meter_config[FRAME_RATE]==0):
            self.sio.emit('getState', {})

            self.meter.updateview(self.metadata if self.updatemetadata else None)
            self.updatemetadata=False

        switch = False
        if self.autoswitchmeter['title'] and self.titleupdate:
            self.titleupdate = False
            switch = True
        if self.autoswitchmeter['album'] and self.albumupdate:
            self.albumupdate = False
            switch = True
        if switch:
            self.switchmeter()
            #self.restart()

        if not self.timer_controlled_random_meter:
            return
               
        if (self.random_meter or self.list_meter) and self.frames == self.frames_before_switch:
            self.frames = 0
            self.restart()

        self.frames += 1
