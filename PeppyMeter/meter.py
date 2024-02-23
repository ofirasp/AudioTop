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

import os
import time
import re
import requests
import io
from netifaces import AF_INET
import netifaces as ni
import socket

from component import Component, TextComponent, ProgressBarComponent
from container import Container
from configfileparser import *
from linear import LinearAnimator
from circular import CircularAnimator
import pygame


class Meter(Container):
    """ The base class for all meters """

    def __init__(self, util, meter_type, meter_parameters, data_source):
        """ Initializer

        :param util: utility class
        :param meter_type: the type of the meter - linear or circular
        :param meter_parameters: meter configuration parameters
        :param data_source: audio data source
        """
        self.util = util
        self.meter_config = util.meter_config
        self.meter_parameters = meter_parameters

        if getattr(util, "config", None):
            self.config = util.config
            self.rect = self.config[SCREEN_RECT]
        else:
            self.rect = self.util.meter_config[SCREEN_RECT]

        self.meter_type = meter_type
        self.ui_refresh_period = meter_parameters[UI_REFRESH_PERIOD]
        self.data_source = data_source
        Container.__init__(self, util, self.rect, (0, 0, 0))
        self.content = None
        self.max_volume = 100.0
        self.total_steps = 100
        self.origin_x = self.origin_y = 0
        self.meter_bounding_box = None
        self.bgr = None
        self.fgr = None
        self.left_sprites = None
        self.right_sprites = None
        self.mono_needle_sprites = None
        self.mono_needle_rects = None
        self.left_needle_sprites = None
        self.right_needle_sprites = None
        self.left_needle_rects = None
        self.right_needle_rects = None
        self.masks = None
        self.channels = 1
        self.meter_x = meter_parameters[METER_X]
        self.meter_y = meter_parameters[METER_Y]
        self.direction = meter_parameters.get(DIRECTION)
        self.indicator_type = meter_parameters.get(INDICATOR_TYPE, None)
        self.flip_left_x = meter_parameters.get(FLIP_LEFT_X, None)
        self.flip_right_x = meter_parameters.get(FLIP_RIGHT_X, None)

    def add_background(self, image_name, meter_x, meter_y):
        """ Position and add background image.

        :param image_name: the name of the background image
        :param meter_x: meter x coordinate
        :param meter_y: meter y coordinate
        """
        img = self.load_image(image_name)
        self.origin_x = meter_x
        self.origin_y = meter_y
        self.meter_bounding_box = img[1].get_rect()
        self.meter_bounding_box.x = self.origin_x
        self.meter_bounding_box.y = self.origin_y
        self.bgr = self.add_image(img, self.origin_x, self.origin_y, self.meter_bounding_box)

    def add_foreground(self, image_name):
        """ Position and add foreground image.
        :param image_name: the name of the foreground image
        """
        if not image_name: return
        img = self.load_image(image_name)
        self.fgr = self.add_image(img, self.origin_x, self.origin_y, self.meter_bounding_box)

    def add_channel(self, image_name, x, y):
        """ Position and add channel indicator image.

        :param image_name: the name of the indicator image
        """
        img = self.load_image(image_name)
        r = img[1].get_rect()
        r.x = self.origin_x + x
        r.y = self.origin_y + y
        self.add_image(img, self.origin_x + x, self.origin_y + y, r)

    def load_image(self, path):
        """ Load image

        :param image_name: the image name
        """
        base_path = self.meter_config[BASE_PATH]
        folder = self.meter_config[SCREEN_INFO][METER_FOLDER]
        path = os.path.join(base_path, folder, path)
        return self.util.load_pygame_image(path)

    def add_image(self, image, x, y, rect=None):
        """ Creates new UI component from provided image and adds it to the UI container.

        :param image: the image object
        :param x: x coordinate of the image top left corner
        :param y: y coordinate of the image top left corner
        :param rect: bounding rectangle of the image
        """
        c = Component(self.util)
        c.content = image
        c.content_x = rect.x
        c.content_y = rect.y
        c.origin_x = x
        c.origin_y = y
        if rect:
            r = rect.copy()
            r.x += self.meter_x
            r.y += self.meter_y
            c.bounding_box = r
        self.add_component(c)
        return c

    def set_volume(self, volume):
        """ Set volume level """

        self.max_volume = volume

    def draw_bgr_fgr(self, rect, comp):
        """ Draw either background or foreground component """
        if not rect: return
        comp.content_x = rect.x
        comp.content_y = rect.y
        comp.bounding_box = rect
        comp.bounding_box = (rect.x - self.origin_x, rect.y - self.origin_y, rect.w, rect.h)
        comp.draw()

    def start(self):
        """ Initialize meter and start meter animation. """

        meter_name = self.meter_config[METER]
        meter_section = self.meter_config[meter_name]
        if meter_section[SCREEN_BGR]:
            img = self.load_image(meter_section[SCREEN_BGR])
            c = Component(self.util)
            c.content = img[1]
            c.content_x = 0
            c.content_y = 0
            c.draw()

        self.reset_bgr_fgr(self.bgr)

        if self.masks:
            self.reset_mask(self.components[1])
            self.reset_mask(self.components[2])

        if self.fgr: self.reset_bgr_fgr(self.fgr)

        super(Meter, self).draw()
        needles = (self.left_needle_sprites, self.right_needle_sprites, self.mono_needle_sprites)
        rects = (self.left_needle_rects, self.right_needle_rects, self.mono_needle_rects)

        if self.meter_type == TYPE_LINEAR:
            self.animator = LinearAnimator(self.data_source, self.components, self, self.ui_refresh_period,
                                           self.direction, self.indicator_type, self.flip_left_x, self.flip_right_x)
        elif self.meter_type == TYPE_CIRCULAR:
            if self.channels == 2:
                self.left = CircularAnimator(self.data_source, self.components[1], self, self.meter_parameters,
                                             needles[0], rects[0],
                                             self.data_source.get_current_left_channel_data,
                                             self.meter_parameters[LEFT_ORIGIN_X], self.meter_parameters[LEFT_ORIGIN_Y])
                self.right = CircularAnimator(self.data_source, self.components[2], self, self.meter_parameters,
                                              needles[1], rects[1],
                                              self.data_source.get_current_right_channel_data,
                                              self.meter_parameters[RIGHT_ORIGIN_X],
                                              self.meter_parameters[RIGHT_ORIGIN_Y])
            else:
                self.mono = CircularAnimator(self.data_source, self.components[1], self, self.meter_parameters,
                                             needles[2], rects[2],
                                             self.data_source.get_current_mono_channel_data,
                                             self.meter_parameters[MONO_ORIGIN_X], self.meter_parameters[MONO_ORIGIN_Y])

    def run(self):
        """ Run the current meter

        :return: list of rectangles for update
        """
        if self.meter_type == TYPE_LINEAR:
            if hasattr(self, "animator") and self.animator:
                return self.animator.run()
        elif self.meter_type == TYPE_CIRCULAR:
            if self.channels == 2:
                if hasattr(self, "left") and self.left and hasattr(self, "right") and self.right:
                    return [self.left.run(), self.right.run()]
            else:
                if hasattr(self, "mono") and self.mono:
                    return [self.mono.run()]

        return None

    def reset_bgr_fgr(self, comp):
        """ Reset background or foreground bounding box

        :param comp: component to reset
        """
        comp.bounding_box = comp.content[1].get_rect()
        comp.content_x = self.origin_x
        comp.content_y = self.origin_y

    def reset_mask(self, comp):
        """ Initialize linear mask. """

        comp.bounding_box.x = comp.content_x
        comp.bounding_box.y = comp.content_y
        w, h = comp.content[1].get_size()
        if w > h:
            comp.bounding_box.w = 1
        else:
            comp.bounding_box.h = 1

    def stop(self):
        """ Stop meter animation """

        if self.meter_type == TYPE_LINEAR:
            self.animator = None
        elif self.meter_type == TYPE_CIRCULAR:
            if self.channels == 2:
                self.left = None
                self.right = None
            else:
                self.mono = None

    def updateview(self,metadata):
        pass


class MetaMeter(Meter):
    def switchcomponent(self, comp, state=None):
        pattern = r'/(.*-)(on|off)(.png)'
        rec = re.compile(pattern)
        m = rec.search(comp.path)
        if m:
            if not state:
                if m.group(2) == 'on':
                    s = rec.sub(r'\1off\3', comp.path)
                else:
                    s = rec.sub(r'\1on\3', comp.path)
            else:
                s = rec.sub(fr'\1{state}\3', comp.path)
            comp.content = self.load_image(s)

    def updateview(self,metadata):

        if self.data_source.get_current_left_channel_data()>80:
            self.switchcomponent(self.redleds[0],"on")
        else:
            self.switchcomponent(self.redleds[0], "off")
        if self.data_source.get_current_right_channel_data()>80:
            self.switchcomponent(self.redleds[1],"on")
        else:
            self.switchcomponent(self.redleds[1], "off")

        if metadata:
            print(metadata)
            codec='flac'
            for s in self.musicservices:
                self.switchcomponent(self.musicservices[s], "off")
            for c in self.codec:
                self.switchcomponent(self.codec[c], "off")
            if 'service' in metadata:
                self.switchcomponent(self.musicservices[metadata['service']],"on")
                codec = self.getcodec(metadata)
            self.switchcomponent(self.codec[codec])
            network = self.getnetwork()
            self.switchcomponent(self.wifi,"on" if network[0] else "off")
            self.switchcomponent(self.eth,"on" if network[1] else "off")
            self.switchcomponent(self.play, "on" if metadata['status'] == 'play' else 'off')
            self.switchcomponent(self.rnd, "on" if metadata['random']  else 'off')
            self.switchcomponent(self.rpt, "on" if metadata['repeat']  else 'off')
            self.switchcomponent(self.inet, "on" if self.isInternet() else 'off')

            self.cover.content = self.getalbumartpath(metadata['albumart'])

            self.metatext.album =  metadata['album']
            self.metatext.artist = metadata['artist']
            self.metatext.title = metadata['title']
            self.metatext.seek = metadata['seek']
            self.metatext.duration = metadata['duration']
            self.metatext.bitrate = metadata['samplerate'] + " " + metadata['bitdepth']
            self.metatext.osversion = self.getosversion();
            self.progressbar.progress = self.metatext.seek/1000/self.metatext.duration*100 if self.metatext.duration!=0 else 0


        self.redrawview()
    def isInternet(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return True
        except:
            return False
    def getnetwork(self):
        allint = ni.interfaces()
        net = [False,False]
        if 'en0' in allint:
            net[0] = AF_INET in ni.ifaddresses('en0')
        if 'en13' in allint:
            net[1] = AF_INET in ni.ifaddresses('en13')
        return net
    def getosversion(self):
        try:
            with open('/etc/os-release',"rt") as osinfo:
                for line in osinfo:
                    if 'VOLUMIO_VERSION' in line:
                        return line.split('=')[1].strip().strip('"')
        except:
            pass
        return "3.611"
    def getcodec(self,metadata):
        if metadata['service'] == 'airplay_emulation':
            return  'aac'
        if metadata['service'] == 'mpd' and 'trackType' in metadata and metadata['trackType'] != 'tidal':
            return metadata['trackType']
        if metadata['service'] == 'tidalconnect' and 'trackType' in metadata:
            return metadata['codec']
        elif 'trackType' in metadata and metadata['trackType'] == 'tidal':
            return 'flac'
        return 'flac'
    def getalbumartpath(self,albumart):
        if not "//extralarge" in albumart or "path=" in albumart:
            if not "http" in albumart:
                albumart = "http://volumio.local:3000" + albumart
            if albumart != self.cover.content[0]:
                return self.loadimagefromurl(albumart)
        else:
            if albumart != self.cover.content[0]:
                return self.load_image(albumart)
        return self.cover.content
    def redrawview(self):
        self.reset_bgr_fgr(self.bgr)
        self.reset_bgr_fgr(self.fgr)
        self.draw()
        pygame.display.update()
    def loadimagefromurl(self,imageurl):
        try:
            r = requests.get(imageurl,timeout=4)
            img = io.BytesIO(r.content)
            img = pygame.image.load(img, "").convert_alpha()
            r = img.get_rect()
            if(r.w!=200 and r.h!=200):
                img = pygame.transform.scale(img, (200, 200))
            comp = (imageurl, img)
        except Exception as ex:
            self.coverurl = "http://volumio.local:3000/albumart"
            comp = self.load_image('/home/volumio/PeppyMeter/icons/albumart.jpg')
        return  comp
    def getimagefrompath(self, path):
        try:
            comp = self.load_image(path)
            r = comp[1].get_rect()
            if (r.w != 200 and r.h != 200):
                img = pygame.transform.scale(comp[1], (200, 200))
                comp = (path, img)
        except Exception as ex:
            path = '../icons/albumart.jpg'
            self.coverurl = "http://127.0.0.1:3000/albumart"
            comp = self.load_image(path)
            r = comp[1].get_rect()
            comp = (path, comp[1])
        return comp

    def add_image_component(self, path, x, y, scale=False):
        if scale:
            img = self.getimagefrompath(path)
        else:
            img = self.load_image(path)
        c = self.add_image(img, 0, 0, self.meter_bounding_box)
        c.content_x = x
        c.content_y = y
        c.path = "/"+path
        return c


class CicularMetaMeter(MetaMeter):
    def add_foreground(self, image_name):
        super().add_foreground(image_name)

        self.cover = self.add_image_component('../icons/albumart.jpg', 540, 150, True)
        self.eth = self.add_image_component('../icons/eth-off.png', 24, 50)
        self.wifi = self.add_image_component('../icons/wifi-off.png', 60, 50)
        self.inet = self.add_image_component('../icons/inet-off.png', 95, 50)
        self.rnd = self.add_image_component('../icons/rnd-off.png', 445, 47)
        self.rpt = self.add_image_component('../icons/rpt-off.png', 485, 47)
        self.play = self.add_image_component('../icons/play-off.png', 410, 51)
        self.redleds = self.add_image_component('../icons/redled-off.png', 480, 100),self.add_image_component('../icons/redled-off.png', 1217, 100)
        self.musicservices = {
            "airplay_emulation": self.add_image_component('../icons/airplay-off.png', 1215, 38),
            "tidalconnect": self.add_image_component('../icons/tidalconnect-off.png', 1185, 45),
            "mpd": self.add_image_component('../icons/hdd-off.png', 1140, 45),
            "volumio": self.add_image_component('../icons/volumio-off.png', 1115, 48),
            "tidal": self.add_image_component('../icons/tidal-off.png', 1058, 33)

        }
        self.codec = {
            "aac": self.add_image_component('../icons/aac-off.png', 922, 43),
            "mqa": self.add_image_component('../icons/mqa-off.png', 890, 45),
            "flac": self.add_image_component('../icons/flac-off.png', 844, 52),
            "dsf": self.add_image_component('../icons/dsd-off.png', 795, 45),
            "mp3": self.add_image_component('../icons/mp3-off.png', 760, 48)

        }

        self.metatext = TextComponent(self.util)
        self.components.append(self.metatext)

        self.progressbar = ProgressBarComponent(self.util)
        self.components.append(self.progressbar)
        self.progressbar.progress = 50
