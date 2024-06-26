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
import math

from component import Component, TextComponent, ProgressBarComponent,TextTunerComponent,TunerProgressBarComponent,\
    TextNadDeckComponent,ProgressReelComponent,TextAkaiDeckComponent,TextTeacDeckComponent,TextPioDeckComponent
from container import Container
from configfileparser import *
from linear import LinearAnimator
from circular import CircularAnimator
import pygame
import logging

from peppyspectrum.spectrum import Spectrum
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

    def updateview(self,metadata,titletime):
        pass


class MetaMeter(Meter):
    def __init__(self, util, meter_type, meter_parameters, data_source):
        super().__init__(util, meter_type, meter_parameters, data_source)
        self.config = util.meter_config[util.meter_config['meter']]
        self.metadatasourcedns = util.meter_config['metadatasourcedns']
        self.usepeak = self.config['icons.usepeak']
        self.peakthreshold = self.config['icons.peakthreshold']
        self.coversize = self.config['cover.size']
        self.usesingle = self.config['icons.usesingle']
        self.musicservices = {}
        self.codecs = {}
        self.codec = None
        self.musicservice = None
        self.playing = False
        self.network = None
        self.infadecover = False
        self.coveralpha = 0

    def fadecover(self):
        if self.infadecover and self.coveralpha<255:
            temp_image = self.newcover[1].copy()
            temp_image.fill((255, 255, 255, self.coveralpha), None, pygame.BLEND_RGBA_MULT)
            self.cover.content = self.cover.content[0],temp_image
            self.redrawview()
            self.coveralpha += 10
            if self.coveralpha>255:
                self.infadecover = False
                self.cover.content = self.newcover
    def fade_in(self, new_image, duration):
        self.infadecover = True
        self.newcover = new_image
        self.coveralpha = 0

    def fade_in1(self, new_image, duration):
        clock = pygame.time.Clock()
        alpha = 0
        step = 255 / (duration * 60)  # Assuming 60 FPS
        while alpha < 255:
            temp_image = new_image[1].copy()
            temp_image.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
            self.screen.blit(temp_image, (self.cover.content_x, self.cover.content_y))
            pygame.display.flip()
            alpha += step
            clock.tick(60)
        self.cover.content = new_image
    def add_foreground(self, image_name):
        if (image_name):
            super().add_foreground(image_name)

        self.iconcolor = self.config['icons.color']
        self.cover = self.add_image_component('../icons/albumart.jpg', *self.config['cover.position'], True)
        self.eth = self.add_image_component('../icons/eth-off.png', *self.config['icons.eth.position'])
        self.wifi = self.add_image_component('../icons/wifi-off.png', *self.config['icons.wifi.position'])
        self.inet = self.add_image_component('../icons/inet-off.png', *self.config['icons.inet.position'])
        self.rnd = self.add_image_component('../icons/rnd-off.png', *self.config['icons.rnd.position'])
        self.rpt = self.add_image_component('../icons/rpt-off.png', *self.config['icons.rpt.position'])
        self.play = self.add_image_component('../icons/play-off.png', *self.config['icons.play.position'])
        if self.usepeak:
            self.addpeakicons()
        if self.usesingle:
            self.codec = self.add_image_component(f'../icons/flac-on{self.iconcolor}.png', *self.config['icons.flac.position'])
            self.musicservice = self.add_image_component(f'../icons/volumio-on{self.iconcolor}.png', *self.config['icons.volumio.position'])
            self.musicservices = {
                "airplay_emulation": None,
                "tidalconnect": None,
                "mpd": None,
                "volumio": None,
                "tidal": None
            }
        else:
            self.musicservices = {
                "airplay_emulation": self.add_image_component('../icons/airplay_emulation-off.png', *self.config['icons.airplay_emulation.position']),
                "tidalconnect": self.add_image_component('../icons/tidalconnect-off.png', *self.config['icons.tidalconnect.position']),
                "mpd": self.add_image_component('../icons/mpd-off.png', *self.config['icons.mpd.position']),
                "volumio": self.add_image_component('../icons/volumio-off.png', *self.config['icons.volumio.position']),
                "tidal": self.add_image_component('../icons/tidal-off.png', *self.config['icons.tidal.position'])
            }
            self.codecs = {
                "aac": self.add_image_component('../icons/aac-off.png', *self.config['icons.aac.position']),
                "mqa": self.add_image_component('../icons/mqa-off.png', *self.config['icons.mqa.position']),
                "flac": self.add_image_component('../icons/flac-off.png', *self.config['icons.flac.position']),
                "dsf": self.add_image_component('../icons/dsf-off.png', *self.config['icons.dsf.position']),
                #"dff": self.add_image_component('../icons/dsf-off.png', *self.config['icons.dsf.position']),
                "mp3": self.add_image_component('../icons/mp3-off.png', *self.config['icons.mp3.position'])
            }

        self.addTextComponent()
        self.addProgressComponent()
    def switchcomponent(self, comp, state=None):
        pattern = r'/(.*-)(on|off).*(.png)'
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
    def addTextComponent(self):
        self.metatext = TextComponent(self.util)
        self.components.append(self.metatext)
    def addpeakicons(self):
        self.redleds = self.add_image_component('../icons/redled-off.png',
                                                *self.config['icons.redledleft.position']), self.add_image_component(
            '../icons/redled-off.png', *self.config['icons.redledright.position'])

    def addProgressComponent(self):
        self.progressbar = ProgressBarComponent(self.util)
        self.components.append(self.progressbar)
    def switchiconpath(self, comp,prefix,postfix):
        pattern = r'/(.*)(/.*-on.*\.png)'
        s = re.sub(pattern,fr'\1/{prefix}-on{postfix}.png', comp.path)
        comp.content = self.load_image(s)
    def run(self):
        r =  super().run()
        if self.usepeak:
            left = self.data_source.get_current_left_channel_data()
            right = self.data_source.get_current_right_channel_data()
            if left and left > self.peakthreshold:
                self.switchcomponent(self.redleds[0], "on")
            else:
                self.switchcomponent(self.redleds[0], "off")
            if right and right > self.peakthreshold:
                self.switchcomponent(self.redleds[1], "on")
            else:
                self.switchcomponent(self.redleds[1], "off")
            self.redleds[1].draw()
            self.redleds[0].draw()
            pygame.display.update([pygame.Rect(self.redleds[1].content_x, self.redleds[1].content_y, 25, 25),
                                   pygame.Rect(self.redleds[0].content_x,self.redleds[0].content_y, 25, 25)])
         #self.redrawview()
        self.fadecover()
        return r

    def stop(self):
        super().stop()
        self.clean()
        self.redrawview()
    def updateview(self,metadata,titletime):
        redrawneeded = False

        osversion = self.getosversion()
        if self.metatext.osversion != osversion:
            self.metatext.osversion = osversion
            redrawneeded = True

        network = self.getnetwork()
        if self.network != network:
            self.network = network
            self.switchcomponent(self.wifi, f"on{self.iconcolor}" if network[0] else "off")
            self.switchcomponent(self.eth, f"on{self.iconcolor}" if network[1] else "off")
            self.switchcomponent(self.inet, f"on{self.iconcolor}" if network[2] else 'off')
            redrawneeded = True

        if self.metatext.seek!=titletime:
            if self.metatext.duration<=titletime:
                self.metatext.seek = titletime
                self.progressbar.progress = self.metatext.seek / 1000 / self.metatext.duration * 100 if self.metatext.duration != 0 else 0
            if self.progressbar.progress > 100:
                self.progressbar.progress = 0
            redrawneeded = True
        if metadata :
            if 'status' in metadata:
                self.playing = metadata['status'] == 'play'
            codec='flac'
            if self.usesingle:
                if 'service' in metadata:
                    codec = self.getcodec(metadata)
                    self.switchiconpath(self.codec,codec,postfix=self.iconcolor)
                    self.switchiconpath(self.musicservice, metadata['service'],postfix=self.iconcolor)
            else:
                for s in self.musicservices:
                    self.switchcomponent(self.musicservices[s], "off")
                for c in self.codecs:
                    self.switchcomponent(self.codecs[c], "off")
                if 'service' in metadata:
                    codec = self.getcodec(metadata)
                    self.switchcomponent(self.musicservices[metadata['service']],"on")
                if not codec in self.codecs:
                    codec='flac'
                self.switchcomponent(self.codecs[codec])

            self.switchcomponent(self.play, f"on{self.iconcolor}" if self.playing else 'off')
            self.switchcomponent(self.rnd, f"on{self.iconcolor}" if 'random' in metadata and metadata['random']  else 'off')
            self.switchcomponent(self.rpt, f"on{self.iconcolor}" if 'repeat' in metadata and metadata['repeat']  else 'off')

            if 'albumart' in metadata:

                newcover = self.getalbumart(metadata['albumart'])
                if newcover[0]!=self.cover.content[0]:
                    self.fade_in(newcover,2)
                    #self.cover.content = newcover
                # self.cover.content[1].set_alpha(0)
                # for alpha in range(0, 255, 1):
                #     self.cover.content[1].set_alpha(alpha)
                #     r = self.cover.content[1].get_rect()
                #     pygame.display.update([pygame.Rect(self.cover.content_x, self.cover.content_y, r.w, r.h)])



            self.metatext.album =  metadata['album'] if 'album' in metadata else '---'
            self.metatext.artist = metadata['artist'] if 'artist' in metadata else '---'
            self.metatext.title = metadata['title'] if 'title' in metadata else '---'
            self.metatext.duration = metadata['duration'] if 'duration' in metadata else 0
            if 'samplerate' in metadata and metadata['samplerate'] and 'bitdepth' in metadata and metadata['bitdepth']:
                if "11.28" in metadata['samplerate']:
                    self.metatext.bitrate = "DSD 256"
                elif "5.64" in metadata['samplerate']:
                    self.metatext.bitrate = "DSD 128"
                elif "2.82" in metadata['samplerate']:
                    self.metatext.bitrate = "DSD 64"
                else:
                    self.metatext.bitrate = metadata['samplerate'].replace(' ','')  + " " + metadata['bitdepth'].replace(' ','')

            redrawneeded = True

        if redrawneeded:
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
        net = [False,False,False]
        if 'eth0' in allint:
            net[1] = AF_INET in ni.ifaddresses('eth0')
        if 'wlan0' in allint:
            net[0] = AF_INET in ni.ifaddresses('wlan0')
        net[2] = self.isInternet()
        return net
    def getosversion(self):
        try:
            with open('/etc/os-release',"rt") as osinfo:
                for line in osinfo:
                    if 'VOLUMIO_VERSION' in line:
                        return line.split('=')[1].strip().strip('"')
        except:
            pass
        return "----"
    def getcodec(self,metadata):
        if metadata['service'] == 'airplay_emulation':
            return  'aac'
        if metadata['service'] == 'mpd' and 'trackType' in metadata and metadata['trackType'] != 'tidal':
            if metadata['trackType']=='dff':
                metadata['trackType']='dsf'
            return metadata['trackType']
        if metadata['service'] == 'tidalconnect' and 'trackType' in metadata:
            return metadata['codec']
        if metadata['service'] == 'webradio':
            metadata['service'] = 'volumio'
            metadata['samplerate'] = "webradio"
            if 'bitrate' in metadata:
                metadata['bitdepth'] = metadata['bitrate']
            return  'mp3'
        if not metadata['service'] in self.musicservices:
            metadata['service'] = 'volumio'
        elif 'trackType' in metadata and metadata['trackType'] == 'tidal':
            metadata['service'] = 'tidal'
            return 'flac'
        return 'flac'
    def getalbumart(self,albumart):
        if not "http" in albumart:
            albumart = f"http://{self.metadatasourcedns}:3000" + albumart
        if not self.cover or albumart != self.cover.content[0]:
            return self.loadimagefromurl(albumart)
        return self.cover.content
    def redrawview(self):
        self.reset_bgr_fgr(self.bgr)
        if self.fgr:
            self.reset_bgr_fgr(self.fgr)
        self.draw()

        pygame.display.update()
    def loadimagefromurl(self,imageurl):
        try:
            r = requests.get(imageurl,timeout=4)
            img = io.BytesIO(r.content)
            img =  pygame.image.load(img).convert_alpha()
            r = img.get_rect()
            if(r.w!=self.coversize and r.h!=self.coversize):
                img = pygame.transform.scale(img, (self.coversize, self.coversize))
            comp = (imageurl, img)
        except Exception as ex:
            logging.warning(f"failed on loading coverart {imageurl} loading default image")
            comp = self.getimagefrompath('../icons/albumart.jpg')
            comp = (imageurl,comp[1])
        return  comp
    def getimagefrompath(self, path):
        try:
            comp = self.load_image(path)
            r = comp[1].get_rect()
            if (r.w != self.coversize and r.h != self.coversize):
                img = pygame.transform.scale(comp[1], (self.coversize, self.coversize))
                comp = (path, img)
            return comp
        except Exception as ex:
            logging.error(f"failed on loading image {path}")
            raise ex


    def add_image_component(self, path, x, y, scale=False):
        if scale:
            img = self.getimagefrompath(path)
        else:
            img = self.load_image(path)
        c = self.add_image(img, 0, 0, self.meter_bounding_box)
        c.content_x = x
        c.content_y = y
        #r = img[1].get_rect()
        #c.imagerect = pygame.Rect(x,y,r.w,r.h)
        c.path = "/"+path
        return c


class MetaCasseteMeter(MetaMeter):
    def __init__(self, util, meter_type, meter_parameters, data_source):
        super().__init__(util, meter_type, meter_parameters, data_source)
        self.angleleft = 0
        self.angleright = 0
        self.rotation_speedleft = 1
        self.rotation_speedright = 5
        self.clearwidth = self.config['icons.casseteclear.width']
        self.clearstartx = 0
        self.clearstatus = 0
        self.prevprogress = 0
        self.frames = 0

    def updateview(self, metadata,titletime):
        self.prevprogress = self.progressbar.progress
        super().updateview(metadata,titletime)
    def run(self):
        self.frames += 1
        r = super().run()
        if self.playing:
            self.casseteAnimation()
            if self.fgr:
                self.reset_bgr_fgr(self.fgr)
        return r
    def add_foreground(self, image_name):
        super().add_foreground(image_name)
        self.image = self.load_image(self.config['icons.casstewheel'])[1]
        self.image_rectright = self.image.get_rect(center=self.config['icons.casstewheelright.position'])
        self.image_rectleft = self.image.get_rect(center=self.config['icons.casstewheelleft.position'])
        self.leftcomp = self.add_image_component(self.config['icons.casstewheel'], self.image_rectleft.x,self.image_rectleft.y)
        self.rightcomp = self.add_image_component(self.config['icons.casstewheel'], self.image_rectright.x, self.image_rectright.y)
        self.area = pygame.Rect(self.image_rectleft.x, self.image_rectleft.y,
                           self.image_rectright.x + self.image_rectright.w ,
                           self.image_rectleft.h)
        self.casseteclear = self.add_image_component(self.config['icons.casseteclear'],
                                                     *self.config['icons.casseteclear.position'])
        self.clearstartx = self.casseteclear.content_x
        self.components.remove(self.progressbar)
        self.casseteAnimation()
        self.redrawview()
    def rotatecomp(self, comp, angle, rect):
        rotated_image = pygame.transform.rotate(self.image, angle)
        rotated_rect = rotated_image.get_rect(center=rect.center)
        comp.content_x = rotated_rect.x
        comp.content_y = rotated_rect.y
        comp.content = (comp.content[0], rotated_image)
    def casseteAnimation(self):
        self.rotatecomp(self.rightcomp, self.angleright, self.image_rectright)
        self.rotatecomp(self.leftcomp, self.angleleft, self.image_rectleft)

        progdiff = self.progressbar.progress - self.prevprogress
        directionfactor = 1 if progdiff >= 0 else -1
        clearspeed = 10
        if math.fabs(progdiff) > 10:
            self.prevprogress += clearspeed * directionfactor
            self.clearstatus = self.prevprogress / 100 * self.clearwidth
            self.rotation_speedleft = 20
            self.rotation_speedright = 20
            self.redrawview()
        else:
            self.clearstatus = self.progressbar.progress / 100 * self.clearwidth
            self.casseteclear.content_x = self.clearstartx - self.clearstatus
            directionfactor = 1
            if self.progressbar.progress < 20:
                self.rotation_speedleft = 1
                self.rotation_speedright = 5
            elif self.progressbar.progress < 35:
                self.rotation_speedleft = 2
                self.rotation_speedright = 4
            elif self.progressbar.progress < 50:
                self.rotation_speedleft = 3
                self.rotation_speedright = 3
            elif self.progressbar.progress < 65:
                self.rotation_speedleft = 4
                self.rotation_speedright = 2
            else:
                self.rotation_speedleft = 5
                self.rotation_speedright = 1
        self.casseteclear.content_x = self.clearstartx - self.clearstatus
        self.angleright += self.rotation_speedright * directionfactor
        if self.angleright >= 360:
            self.angleright = 0
        self.angleleft += self.rotation_speedleft * directionfactor
        if self.angleleft >= 360:
            self.angleleft = 0
        self.leftcomp.draw()
        self.rightcomp.draw()
        self.casseteclear.draw()
        pygame.display.update([self.area])
        #pygame.display.update([pygame.Rect(0, 0, 1200, 800)])
class MetaNadDeckMeter(MetaCasseteMeter):
    def addTextComponent(self):
        self.metatext = TextNadDeckComponent(self.util)
        self.components.append(self.metatext)
class MetaPioReelMeter(MetaCasseteMeter):
    def casseteAnimation(self):
        if self.frames % 2 != 0:
            return
        self.rotatecomp(self.rightcomp, self.angleright, self.image_rectright)
        self.rotatecomp(self.leftcomp, self.angleleft, self.image_rectleft)

        progdiff = self.progressbar.progress - self.prevprogress
        directionfactor = 1 if progdiff >= 0 else -1
        clearspeed = 10
        if math.fabs(progdiff) > 10:
            self.progressbar.inff = True
            self.prevprogress += clearspeed * directionfactor
            self.rotation_speedleft = 20
            self.rotation_speedright = 20
            self.progressbar.ffprogress += clearspeed * directionfactor
            self.redrawview()
        else:
            self.progressbar.ffprogress = self.progressbar.progress
            self.progressbar.inff = False
            directionfactor = 1
            if self.progressbar.progress < 20:
                self.rotation_speedleft = 1
                self.rotation_speedright = 5
            elif self.progressbar.progress < 35:
                self.rotation_speedleft = 2
                self.rotation_speedright = 4
            elif self.progressbar.progress < 50:
                self.rotation_speedleft = 3
                self.rotation_speedright = 3
            elif self.progressbar.progress < 65:
                self.rotation_speedleft = 4
                self.rotation_speedright = 2
            else:
                self.rotation_speedleft = 5
                self.rotation_speedright = 1
        self.rotation_speedright*=2
        self.rotation_speedleft*=2
        self.angleright += self.rotation_speedright * directionfactor
        if self.angleright >= 360:
            self.angleright = 0
        self.angleleft += self.rotation_speedleft * directionfactor
        if self.angleleft >= 360:
            self.angleleft = 0

        self.reset_bgr_fgr(self.bgr)
        self.draw()
        pygame.display.update([self.image_rectright,self.image_rectleft])


    def addpeakicons(self):
        self.redleds = self.add_image_component('../icons/pioled-off.png',
                                                *self.config['icons.redledleft.position']), self.add_image_component(
            '../icons/pioled-off.png', *self.config['icons.redledright.position'])

    def addProgressComponent(self):
        self.progressbar = ProgressReelComponent(self.util,(649, 155),(1119, 155),60,0.9)
        self.components.append(self.progressbar)

    def add_foreground(self, image_name):
        MetaMeter.add_foreground(self, image_name)
        self.image = self.load_image(self.config['icons.casstewheel'])[1]
        self.image_rectright = self.image.get_rect(center=self.config['icons.casstewheelright.position'])
        self.image_rectleft = self.image.get_rect(center=self.config['icons.casstewheelleft.position'])
        self.leftcomp = self.add_image_component(self.config['icons.casstewheel'], self.image_rectleft.x,self.image_rectleft.y)
        self.rightcomp = self.add_image_component(self.config['icons.casstewheel'], self.image_rectright.x,self.image_rectright.y)

        self.area = pygame.Rect(self.image_rectleft.x, self.image_rectleft.y,
                                self.image_rectright.x + self.image_rectright.w,
                                self.image_rectleft.h)
        self.casseteAnimation()

        self.redrawview()

class MetaSpectrumMeter(MetaMeter):
    def __init__(self, util, meter_type, meter_parameters, data_source):
        super().__init__(util, meter_type, meter_parameters, data_source)
        self.pm = Spectrum(None, True,self.util,self.config)

        #self.pm.callback_start = lambda x: self.pm.clean_draw_update()
        self.pm.start()
        self.framecount=0

    def start(self):
        super().start()
        self.pm.draw()
    def stop(self):
        super().stop()
        self.pm.stop()
    def run(self):

        self.framecount += 1
        if self.framecount == 3:
            self.framecount = 0
            self.pm.get_data()
            self.pm.clean_draw_update()
        #self.draw()


        if self.pm.seconds >= self.pm.config[UPDATE_PERIOD]:
            self.pm.seconds = 0
            # self.pm.refresh()
        #pygame.display.update()
        self.pm.seconds += 0.1
        self.fadecover()
    def redrawview(self):
        self.reset_bgr_fgr(self.bgr)
        if self.fgr:
            self.reset_bgr_fgr(self.fgr)
        self.draw()
        self.pm.clean_draw_update()
        pygame.display.update()

class MetaMSpectrumWithMeter(MetaSpectrumMeter):
    def run(self):
        r = Meter.run(self)
        self.reset_bgr_fgr(self.bgr)
        if self.fgr:
            self.reset_bgr_fgr(self.fgr)

        super().run()

        return r

class TunerSpectrumWithMeter(MetaMSpectrumWithMeter):
    def add_foreground(self, image_name):
        super().add_foreground(image_name)

        self.tunerimage = self.load_image('tunerneedle.png')[1]
        self.tunerimage_rect = self.tunerimage.get_rect(center=(340,95))
        self.tunercomp = self.add_image_component('tunerneedle.png', 340, 95)

        self.tunerAnimation()
        self.redrawview()
    def addTextComponent(self):
        self.metatext = TextTunerComponent(self.util)
        self.components.append(self.metatext)

    def addProgressComponent(self):
        self.progressbar = TunerProgressBarComponent(self.util)
        self.components.append(self.progressbar)
    def tunerAnimation(self):

        addx =340+ (self.progressbar.progress/100)*300

        self.tunercomp.content_x =addx

    def run(self):
        r = super().run()
        if self.playing:
            self.tunerAnimation()

        return r
    def updateview(self, metadata,titletime):
        self.prevprogress = self.progressbar.progress
        super().updateview(metadata,titletime)


class MetaAkaiDeckMeter(MetaPioReelMeter,MetaMSpectrumWithMeter):

    def add_foreground(self, image_name):
        right = self.config['icons.casstewheelright.position']
        left = self.config['icons.casstewheelleft.position']
        self.progressbar = ProgressReelComponent(self.util,left,right, 30, 0.4)
        self.components.append(self.progressbar)
        self.image = self.load_image(self.config['icons.casstewheel'])[1]
        self.image_rectright = self.image.get_rect(center=right)
        self.image_rectleft = self.image.get_rect(center=left)
        self.leftcomp = self.add_image_component(self.config['icons.casstewheel'], self.image_rectleft.x,
                                                 self.image_rectleft.y)
        self.rightcomp = self.add_image_component(self.config['icons.casstewheel'], self.image_rectright.x,
                                                  self.image_rectright.y)

        self.area = pygame.Rect(self.image_rectleft.x, self.image_rectleft.y,
                                self.image_rectright.x + self.image_rectright.w,
                                self.image_rectleft.h)

        MetaMeter.add_foreground(self, image_name)
        self.casseteAnimation()

        self.redrawview()
    def addTextComponent(self):
        self.metatext = TextAkaiDeckComponent(self.util)
        self.components.append(self.metatext)
    def addProgressComponent(self):
        pass

class MetaTeacDeckMeter(MetaAkaiDeckMeter):

    def add_foreground(self, image_name):
        right = self.config['icons.casstewheelright.position']
        left = self.config['icons.casstewheelleft.position']
        self.progressbar = ProgressReelComponent(self.util,left,right, 30, 0.35)
        self.components.append(self.progressbar)
        self.image = self.load_image(self.config['icons.casstewheel'])[1]
        self.image_rectright = self.image.get_rect(center=right)
        self.image_rectleft = self.image.get_rect(center=left)
        self.leftcomp = self.add_image_component(self.config['icons.casstewheel'], self.image_rectleft.x,
                                                 self.image_rectleft.y)
        self.rightcomp = self.add_image_component(self.config['icons.casstewheel'], self.image_rectright.x,
                                                  self.image_rectright.y)

        self.area = pygame.Rect(self.image_rectleft.x, self.image_rectleft.y,
                                self.image_rectright.x + self.image_rectright.w,
                                self.image_rectleft.h)

        MetaMeter.add_foreground(self, image_name)
        self.casseteAnimation()

        self.redrawview()
    def addTextComponent(self):
        self.metatext = TextTeacDeckComponent(self.util)
        self.components.append(self.metatext)
    def addProgressComponent(self):
        pass

class MetaPioDeckMeter(MetaPioReelMeter):
    def addpeakicons(self):
        self.redleds = self.add_image_component('../icons/piodeckled-off.png',
                                                *self.config['icons.redledleft.position']), self.add_image_component(
            '../icons/piodeckled-off.png', *self.config['icons.redledright.position'])
    def add_foreground(self, image_name):
        right = self.config['icons.casstewheelright.position']
        left = self.config['icons.casstewheelleft.position']
        self.progressbar = ProgressReelComponent(self.util,left,right, 30, 0.25)
        self.components.append(self.progressbar)
        self.image = self.load_image(self.config['icons.casstewheel'])[1]
        self.image_rectright = self.image.get_rect(center=right)
        self.image_rectleft = self.image.get_rect(center=left)
        self.leftcomp = self.add_image_component(self.config['icons.casstewheel'], self.image_rectleft.x,
                                                 self.image_rectleft.y)
        self.rightcomp = self.add_image_component(self.config['icons.casstewheel'], self.image_rectright.x,
                                                  self.image_rectright.y)

        self.area = pygame.Rect(self.image_rectleft.x, self.image_rectleft.y,
                                self.image_rectright.x + self.image_rectright.w,
                                self.image_rectleft.h)

        MetaMeter.add_foreground(self, image_name)
        self.casseteAnimation()

        self.redrawview()
    def addTextComponent(self):
        self.metatext = TextPioDeckComponent(self.util)
        self.components.append(self.metatext)
    def addProgressComponent(self):
        pass

    def run(self):
        r = Meter.run(self)
        self.reset_bgr_fgr(self.bgr)
        if self.fgr:
            self.reset_bgr_fgr(self.fgr)
        super().run()
        return r


class MetaPhonoMeter(MetaMeter):
    def addpeakicons(self):
        self.redleds = self.add_image_component('../icons/pioled-off.png',
                                                *self.config['icons.redledleft.position']), self.add_image_component(
            '../icons/pioled-off.png', *self.config['icons.redledright.position'])
    def __init__(self, util, meter_type, meter_parameters, data_source):
        super().__init__(util, meter_type, meter_parameters, data_source)
        self.prevprogress = 0
        self.frames = 0
        self.rotateangle = 0
        self.turnarmstep = 0



    def run(self):
        self.frames += 1
        r = super().run()
        if self.playing and not self.infadecover :
            self.phonoAnimation()
        return r


    def phonoAnimation(self):
        if self.frames % 2 != 0:
            return
        self.rotateangle-=20
        steps =12- 24*(self.progressbar.progress/100)
        self.rotatecomp(self.cover, self.rotateangle, self.cover_rect,self.newcover[1],(0,0))
        if self.frames % 20 == 0:
            self.rotatecomp(self.turnarm, steps, self.turnarm_rect, self.turnarmorig, (-36+steps/2, 35+steps/2))
        self.reset_bgr_fgr(self.fgr)
        self.reset_bgr_fgr(self.bgr)
        self.draw()
        pygame.display.update([self.cover_rect,self.turnarm_rect])

    def rotatecomp(self, comp, angle, rect,image,pivot=(0,0)):
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rect = rotated_image.get_rect(center=(rect.center[0]+pivot[0],rect.center[1]+pivot[1]))
        comp.content_x = rotated_rect.x+pivot[0]
        comp.content_y = rotated_rect.y+pivot[1]
        comp.content = (comp.content[0], rotated_image)
    def add_foreground(self, image_name):
        self.iconcolor = self.config['icons.color']
        self.cover = self.add_image_component('../icons/albumart.jpg', *self.config['cover.position'], True)
        self.cover_rect = self.cover.content[1].get_rect(center=(197, 204))

        self.eth = self.add_image_component('../icons/eth-off.png', *self.config['icons.eth.position'])
        self.wifi = self.add_image_component('../icons/wifi-off.png', *self.config['icons.wifi.position'])
        self.inet = self.add_image_component('../icons/inet-off.png', *self.config['icons.inet.position'])
        self.rnd = self.add_image_component('../icons/rnd-off.png', *self.config['icons.rnd.position'])
        self.rpt = self.add_image_component('../icons/rpt-off.png', *self.config['icons.rpt.position'])
        self.play = self.add_image_component('../icons/play-off.png', *self.config['icons.play.position'])
        if self.usepeak:
            self.addpeakicons()
        if self.usesingle:
            self.codec = self.add_image_component(f'../icons/flac-on{self.iconcolor}.png',
                                                  *self.config['icons.flac.position'])
            self.musicservice = self.add_image_component(f'../icons/volumio-on{self.iconcolor}.png',
                                                         *self.config['icons.volumio.position'])
            self.musicservices = {
                "airplay_emulation": None,
                "tidalconnect": None,
                "mpd": None,
                "volumio": None,
                "tidal": None
            }
        else:
            self.musicservices = {
                "airplay_emulation": self.add_image_component('../icons/airplay_emulation-off.png',
                                                              *self.config['icons.airplay_emulation.position']),
                "tidalconnect": self.add_image_component('../icons/tidalconnect-off.png',
                                                         *self.config['icons.tidalconnect.position']),
                "mpd": self.add_image_component('../icons/mpd-off.png', *self.config['icons.mpd.position']),
                "volumio": self.add_image_component('../icons/volumio-off.png',
                                                    *self.config['icons.volumio.position']),
                "tidal": self.add_image_component('../icons/tidal-off.png', *self.config['icons.tidal.position'])
            }
            self.codecs = {
                "aac": self.add_image_component('../icons/aac-off.png', *self.config['icons.aac.position']),
                "mqa": self.add_image_component('../icons/mqa-off.png', *self.config['icons.mqa.position']),
                "flac": self.add_image_component('../icons/flac-off.png', *self.config['icons.flac.position']),
                "dsf": self.add_image_component('../icons/dsf-off.png', *self.config['icons.dsf.position']),
                # "dff": self.add_image_component('../icons/dsf-off.png', *self.config['icons.dsf.position']),
                "mp3": self.add_image_component('../icons/mp3-off.png', *self.config['icons.mp3.position'])
            }

        self.addTextComponent()
        self.addProgressComponent()

        if (image_name):
            Meter.add_foreground(self,image_name)
        self.turnarm = self.add_image_component('phono-turnarm3.png', 199, 28)
        self.turnarmorig =  self.turnarm.content[1].copy()
        self.turnarm_rect = self.turnarm.content[1].get_rect(center=(421, 108))
        # self.image = self.load_image(self.config['icons.casstewheel'])[1]
        # self.image_rectright = self.image.get_rect(center=self.config['icons.casstewheelright.position'])
        # self.image_rectleft = self.image.get_rect(center=self.config['icons.casstewheelleft.position'])
        # self.leftcomp = self.add_image_component(self.config['icons.casstewheel'], self.image_rectleft.x,self.image_rectleft.y)
        # self.rightcomp = self.add_image_component(self.config['icons.casstewheel'], self.image_rectright.x, self.image_rectright.y)
        # self.area = pygame.Rect(self.image_rectleft.x, self.image_rectleft.y,
        #                    self.image_rectright.x + self.image_rectright.w ,
        #                    self.image_rectleft.h)
        # self.casseteclear = self.add_image_component(self.config['icons.casseteclear'],
        #                                              *self.config['icons.casseteclear.position'])
        # self.clearstartx = self.casseteclear.content_x

        self.components.remove(self.progressbar)
        #self.casseteAnimation()
        #self.redrawview()
