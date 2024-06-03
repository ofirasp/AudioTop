#! /usr/bin/python3
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

import pygame
import os
import sys
import logging
import pickle
from meterutil import MeterUtil
from pygame.time import Clock
from vumeter import Vumeter,PLAYING,STOPPED,STOPPING,STARTPLAYING
from datasource import DataSource, SOURCE_NOISE, SOURCE_PIPE, SOURCE_HTTP
from serialinterface import SerialInterface
from i2cinterface import I2CInterface
from pwminterface import PWMInterface
from httpinterface import HTTPInterface
from screensavermeter import ScreensaverMeter
from configfileparser import *
import time
import signal
import os
import settings
testMode = not "linux" in sys.platform
try:
    os.chdir("/data/plugins/user_interface/audiotop/PeppyMeter")
except:
    pass
class Peppymeter(ScreensaverMeter):
    """ Peppy Meter class """
    
    def __init__(self,settings, util=None, standalone=False, timer_controlled_random_meter=True):
        """ Initializer
        
        :param util: utility object
        :param standalone: True - standalone version, False - part of Peppy player
        """
        ScreensaverMeter.__init__(self)
        self.autoswitchmeter = {'title':settings["config_switch_meter_on_title"]['value'],
                                'album':settings["config_switch_meter_on_album"]['value'],
                                'restart':settings["config_switch_meter_on_restart"]['value']}
        if util:
            self.util = util
        else:
            self.util = MeterUtil()

        self.running = False
        self.use_vu_meter = getattr(self.util, USE_VU_METER, None)
        
        self.name = "peppymeter"

        parser = ConfigFileParser()
        self.util.meter_config = parser.meter_config
        self.util.exit_function = self.exit
        self.outputs = {}
        self.timer_controlled_random_meter = timer_controlled_random_meter

        self.audiotopPID = 0 if testMode else int(input())
        if standalone:
            if self.util.meter_config[USE_LOGGING]:
                log_handlers = []
                try:
                    log_handlers.append(logging.StreamHandler(sys.stdout))
                    log_handlers.append(logging.FileHandler(filename="peppymeter.log", mode='w'))
                    level = logging.NOTSET if self.util.meter_config['use.loglevel'] != 'Warning' else logging.WARNING
                    logging.basicConfig(
                        level=level,
                        format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
                        handlers=log_handlers
                    )
                    logging.info("Peppymeter started")
                except:
                    pass
            else:
                logging.disable(logging.CRITICAL)
        self.persiststate = {"meter.index":0,"meter.name":self.util.meter_config[METER]}
        self.meterlist = self.util.meter_config["meter.list"].split(",")
        try:
            with  open("state.p", "rb") as f:
                self.persiststate = pickle.load(f)
                if  not self.autoswitchmeter["album"] and not self.autoswitchmeter["title"] and self.autoswitchmeter["restart"]:
                    self.persiststate["meter.index"] = (self.persiststate["meter.index"] + 1) % len(self.meterlist)

                self.util.meter_config[METER] = self.meterlist[self.persiststate["meter.index"]]



        except :
            self.savepersiststate()



        # no VU Meter support for Windows
        if "win" in sys.platform and self.util.meter_config[DATA_SOURCE][TYPE] == SOURCE_PIPE:
            self.util.meter_config[DATA_SOURCE][TYPE] = SOURCE_NOISE
        
        self.data_source = DataSource(self.util.meter_config)
        if self.util.meter_config[DATA_SOURCE][TYPE] or self.use_vu_meter == True:
            self.data_source.start_data_source()
        
        if self.util.meter_config[OUTPUT_DISPLAY]:
            self.meter = self.output_display(self.data_source)
            self.meter.meterlist = self.meterlist

        if self.util.meter_config[OUTPUT_SERIAL]:
            self.outputs[OUTPUT_SERIAL] = SerialInterface(self.util.meter_config, self.data_source)
            
        if self.util.meter_config[OUTPUT_I2C]:
            self.outputs[OUTPUT_I2C] = I2CInterface(self.util.meter_config, self.data_source)
            
        if self.util.meter_config[OUTPUT_PWM]:
            self.outputs[OUTPUT_PWM] = PWMInterface(self.util.meter_config, self.data_source)

        if self.util.meter_config[OUTPUT_HTTP]:
            self.outputs[OUTPUT_HTTP] = HTTPInterface(self.util.meter_config, self.data_source)

        self.start_interface_outputs()

        signal.signal(signal.SIGUSR1, self.gotosleep)
        signal.signal(signal.SIGUSR2, self.switchmeter)

        logging.debug("PeppyMeter initialized")
    def gotosleep(self,a,b):
        print(a,b)
        self.stop()
        self.running = False

    def output_display(self, data_source):
        """ Initialize display
        
        :data_source: data source
        :return: graphical VU Meter
        """
        meter = Vumeter(self.util, data_source, self.timer_controlled_random_meter,self.autoswitchmeter,self.switchmeter)
        meter.audiotopPID = self.audiotopPID
        meter.testMode = testMode
        self.current_image = None
        self.update_period = meter.get_update_period()
        
        return meter
    
    def init_display(self):
        """ Initialize Pygame display """

        screen_w = self.util.meter_config[SCREEN_INFO][WIDTH]
        screen_h = self.util.meter_config[SCREEN_INFO][HEIGHT]
        depth = self.util.meter_config[SCREEN_INFO][DEPTH]
        
        os.environ["SDL_FBDEV"] = self.util.meter_config[SDL_ENV][FRAMEBUFFER_DEVICE]

        if self.util.meter_config[SDL_ENV][MOUSE_ENABLED]:
            os.environ["SDL_MOUSEDEV"] = self.util.meter_config[SDL_ENV][MOUSE_DEVICE]
            os.environ["SDL_MOUSEDRV"] = self.util.meter_config[SDL_ENV][MOUSE_DRIVER]
        else:
            os.environ["SDL_NOMOUSE"] = "1"
        
        if not self.util.meter_config[OUTPUT_DISPLAY]:
            os.environ["SDL_VIDEODRIVER"] = self.util.meter_config[SDL_ENV][VIDEO_DRIVER]
            os.environ["DISPLAY"] = self.util.meter_config[SDL_ENV][VIDEO_DISPLAY]
            pygame.display.init()
            pygame.font.init()
            if self.util.meter_config[SDL_ENV][DOUBLE_BUFFER]:
                self.util.PYGAME_SCREEN = pygame.display.set_mode((1,1), pygame.DOUBLEBUF, depth)
            else:
                self.util.PYGAME_SCREEN = pygame.display.set_mode((1,1))
            return
        
        if "win" not in sys.platform:
            if not self.util.meter_config[SDL_ENV][VIDEO_DRIVER] == "dummy":
                os.environ["SDL_VIDEODRIVER"] = self.util.meter_config[SDL_ENV][VIDEO_DRIVER]
            os.environ["DISPLAY"] = self.util.meter_config[SDL_ENV][VIDEO_DISPLAY]
            pygame.display.init()
            pygame.mouse.set_visible(False)
        else:            
            pygame.init()
            pygame.display.set_caption("Peppy Meter")

        pygame.font.init()

        if self.util.meter_config[SDL_ENV][DOUBLE_BUFFER]:
            if self.util.meter_config[SDL_ENV][NO_FRAME]:
                self.util.PYGAME_SCREEN = pygame.display.set_mode((screen_w, screen_h), pygame.DOUBLEBUF | pygame.NOFRAME, depth)
            else:
                self.util.PYGAME_SCREEN = pygame.display.set_mode((screen_w, screen_h), pygame.DOUBLEBUF, depth)
        else:
            if self.util.meter_config[SDL_ENV][NO_FRAME]:
                self.util.PYGAME_SCREEN = pygame.display.set_mode((screen_w, screen_h), pygame.NOFRAME)
            else:
                self.util.PYGAME_SCREEN = pygame.display.set_mode((screen_w, screen_h))

        self.util.meter_config[SCREEN_RECT] = pygame.Rect(0, 0, screen_w, screen_h)
    
    def start_interface_outputs(self):
        """ Starts writing to interfaces """

        for v in self.outputs.values():
            v.start_writing()
    
    def start(self):
        """ Start VU meter. This method called by Peppy Meter to start meter """

        pygame.event.clear()
        if self.util.meter_config[DATA_SOURCE][TYPE] == SOURCE_PIPE or self.use_vu_meter == True:
            self.data_source.start_data_source()
        self.meter.start()
        pygame.display.update(self.util.meter_config[SCREEN_RECT])

        for v in self.outputs.values():
            v.start_writing()

    def start_display_output(self):
        """ Start thread for graphical VU meter """
        
        pygame.event.clear()
        clock = Clock()
        self.meter.start()
        pygame.display.update(self.util.meter_config[SCREEN_RECT])
        self.running  = True

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                    keys = pygame.key.get_pressed() 
                    if (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]) and event.key == pygame.K_c:
                        self.running = False
                elif event.type == pygame.MOUSEBUTTONUP and (self.util.meter_config[EXIT_ON_TOUCH] or self.util.meter_config[STOP_DISPLAY_ON_TOUCH]):
                    self.running = False
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    try:
                        knobmeterto=self.util.meter_config[self.util.meter_config[METER]]["knobs.selectmeterto"]
                        knobmeterfrom = self.util.meter_config[self.util.meter_config[METER]]["knobs.selectmeterfrom"]
                        knobpowerto = self.util.meter_config[self.util.meter_config[METER]]["knobs.powerto"]
                        knobpowerfrom = self.util.meter_config[self.util.meter_config[METER]]["knobs.powerfrom"]
                        if (knobmeterfrom[0]< pos[0] < knobmeterto[0]) and (knobmeterfrom[1]< pos[1] < knobmeterto[1]):
                            self.switchmeter()
                        if (knobpowerfrom[0] < pos[0] < knobpowerto[0]) and (knobpowerfrom[1] < pos[1] < knobpowerto[1]):
                            self.running = False
                    except Exception as ex:
                        self.switchmeter()
            if self.meter.playerstatus == PLAYING or self.meter.playerstatus==STOPPING:
                self.refresh()
            elif self.meter.playerstatus == STOPPED and self.meter.meter:
                self.meter.meter.playing = False
            #elif self.meter.playerstatus == STARTPLAYING:
                #self.restart()
            areas = self.meter.run()
            pygame.display.update(areas)

            clock.tick(self.util.meter_config[FRAME_RATE])
        if self.util.meter_config[STOP_DISPLAY_ON_TOUCH]:
            self.meter.stop()
            pygame.quit()
        else:
            self.meter.pauseplayer()
            self.meter.stop()
            pygame.quit()
            time.sleep(0.5)
            self.exit()
    def switchmeter(self,a=None,b=None):
        self.persiststate["meter.index"] = (self.persiststate["meter.index"] + 1) % len(self.meterlist)
        self.savepersiststate()
        self.util.meter_config[METER] =   self.meterlist[self.persiststate["meter.index"]] #self.meterlist[3]#
        self.meter.stop()
        time.sleep(0.2)
        current = self.meter.util.PYGAME_SCREEN
        self.meter.util.PYGAME_SCREEN = self.meter.util.PYGAME_SCREEN.copy()
        self.meter.meter = None
        self.meter.start()
        time.sleep(0.2)
        next = self.meter.util.PYGAME_SCREEN.copy()
        self.meter.util.PYGAME_SCREEN = current
        for comp in self.meter.meter.components:
            comp.screen = current
        if hasattr(self.meter.meter, "pm"):
            for comp in self.meter.meter.pm.components:
                comp.screen = current
        self.fadein(current, next)
        pygame.display.flip()

    # Function to create a fade in effect
    def fadein(self,surface1, surface2, steps=20):
        screen = self.meter.util.PYGAME_SCREEN
        for alpha in range(0, 255, steps):
            # Set the alpha of the second surface
            surface2.set_alpha(alpha)
            # Draw the first surface
            screen.blit(surface1, (0, 0))
            # Draw the second surface on top with increasing alpha
            screen.blit(surface2, (0, 0))
            # Update the display
            pygame.display.flip()
            pygame.time.delay(60)
        screen.blit(surface2, (0, 0))
        pygame.display.flip()

    def savepersiststate(self):
        with open("state.p", "wb") as f:
            pickle.dump(self.persiststate, f)
    def stop(self):
        """ Stop meter animation. """

        if not self.use_vu_meter:
            for v in self.outputs.values():
                v.stop_writing()

            self.data_source.stop_data_source()

        self.meter.stop()
    
    def restart(self):
        """ Restart random meter """

        self.meter.restart()

    def refresh(self):
        """ Refresh meter. Used to switch from one random meter to another. """
        
        self.meter.refresh()

    def set_volume(self, volume):
        """ Set volume level.

        :param volume: new volume level
        """
        self.data_source.volume = volume
    
    def exit(self):
        """ Exit program """
        
        for v in self.outputs.values():
            v.stop_writing()
        pygame.quit()

        if hasattr(self, "malloc_trim"):
            self.malloc_trim()
        self.meter.diconnectsocketio()
        os._exit(0)

    def set_visible(self, flag):
        """ Set visible/invisible flag.

        :param flag: True - visible, False - invisible
        """
        pass


if __name__ == "__main__":
    """ This is called by stand-alone PeppyMeter """
   # sm = Spectrum(None, True)
   # sm.callback_start = lambda self : sm.clean_draw_update()
   # sm.start()


    settings = settings.Settings()
    settings.retreive()
    pm = Peppymeter(settings,standalone=True)
    source = pm.util.meter_config[DATA_SOURCE][TYPE]
    if source == SOURCE_HTTP:
        try:
            f = open(os.devnull, 'w')
            sys.stdout = sys.stderr = f
            from webserver import WebServer
            web_server = WebServer(pm)
        except Exception as e:
            logging.debug(e)

    if source != SOURCE_PIPE:
        pm.data_source.start_data_source()
        
    pm.init_display()
        
    if pm.util.meter_config[OUTPUT_DISPLAY]:
        pm.start_display_output()
