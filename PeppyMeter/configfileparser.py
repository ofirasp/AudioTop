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
from ast import literal_eval as make_tuple

from configparser import ConfigParser

CURRENT = "current"
SCREEN_INFO = "screen.info"
BASE_FOLDER = "base.folder"
METER_FOLDER = "meter.folder"
WIDTH = "width"
HEIGHT = "height"
DEPTH = "depth"
FRAME_RATE = "frame.rate"
SCREEN_WIDTH = "screen.width"
SCREEN_HEIGHT = "screen.height"
SCREEN_RECT = "screen.rect"
EXIT_ON_TOUCH = "exit.on.touch"
STOP_DISPLAY_ON_TOUCH = "stop.display.on.touch"
OUTPUT_DISPLAY = "output.display"
OUTPUT_SERIAL = "output.serial"
OUTPUT_I2C = "output.i2c"
OUTPUT_PWM = "output.pwm"
OUTPUT_HTTP = "output.http"

SERIAL_INTERFACE = "serial.interface"
DEVICE_NAME = "device.name"
BAUD_RATE = "baud.rate"
INCLUDE_TIME = "include.time"
UPDATE_PERIOD = "update.period"

I2C_INTERFACE = "i2c.interface"
PORT = "port"
LEFT_CHANNEL_ADDRESS = "left.channel.address"
RIGHT_CHANNEL_ADDRESS = "right.channel.address"
OUTPUT_SIZE = "output.size"

HTTP_INTERFACE = "http.interface"
TARGET_URL = "target.url"

PWM_INTERFACE = "pwm.interface"
FREQUENCY = "frequency"
GPIO_PIN_LEFT = "gpio.pin.left"
GPIO_PIN_RIGHT = "gpio.pin.right"

SDL_ENV = "sdl.env"
FRAMEBUFFER_DEVICE = "framebuffer.device"
MOUSE_DEVICE = "mouse.device"
MOUSE_DRIVER = "mouse.driver"
MOUSE_ENABLED = "mouse.enabled"
VIDEO_DRIVER = "video.driver"
VIDEO_DISPLAY = "video.display"
DOUBLE_BUFFER = "double.buffer"
NO_FRAME = "no.frame"

SMOOTH_BUFFER_SIZE = "smooth.buffer.size"
USE_LOGGING = "use.logging"
USE_CACHE = "use.cache"
USAGE = "usage"
USE_VU_METER = "vu.meter"
METER = "meter"
DATA_SOURCE = "data.source"
TYPE = "type"
POLLING_INTERVAL = "polling.interval"
PIPE_NAME = "pipe.name"
VOLUME_CONSTANT = "volume.constant"
VOLUME_MIN = "volume.min"
VOLUME_MAX = "volume.max"
VOLUME_MAX_IN_PIPE = "volume.max.in.pipe"
STEP = "step"
MONO_ALGORITHM = "mono.algorithm"
STEREO_ALGORITHM = "stereo.algorithm"
METER_TYPE = "meter.type"
SPECTRUM_TYPE = "spectrum.type"
CHANNELS = "channels"
DIRECTION = "direction"
FLIP_LEFT_X = "flip.left.x"
FLIP_RIGHT_X = "flip.right.x"
UI_REFRESH_PERIOD = "ui.refresh.period"
BGR_FILENAME = "bgr.filename"
FGR_FILENAME = "fgr.filename"
INDICATOR_FILENAME = "indicator.filename"
LEFT_X = "left.x"
LEFT_Y = "left.y"
RIGHT_X = "right.x"
RIGHT_Y = "right.y"
MONO_X = "mono.x"
MONO_Y = "mono.y"       
POSITION_REGULAR = "position.regular"
POSITION_OVERLOAD = "position.overload"
STEP_WIDTH_REGULAR = "step.width.regular"
STEP_WIDTH_OVERLOAD = "step.width.overload"  
STEPS_PER_DEGREE = "steps.per.degree"
START_ANGLE = "start.angle"
STOP_ANGLE = "stop.angle"
DISTANCE = "distance"
MONO_ORIGIN_X = "mono.origin.x"
MONO_ORIGIN_Y = "mono.origin.y"
LEFT_CENTER_X = "left.center.x"
LEFT_CENTER_Y = "left.center.y"
LEFT_ORIGIN_X = "left.origin.x"
LEFT_ORIGIN_Y = "left.origin.y"
RIGHT_CENTER_X = "right.center.x"
RIGHT_CENTER_Y = "right.center.y"
RIGHT_ORIGIN_X = "right.origin.x"
RIGHT_ORIGIN_Y = "right.origin.y"
METER_NAMES = "meter.names"
RANDOM_METER_INTERVAL = "random.meter.interval"
BASE_PATH = "base.path"
METER_X = "meter.x"
METER_Y = "meter.y"
SCREEN_BGR = "screen.bgr"

FILE_CONFIG = "config.txt"
FILE_METER_CONFIG = "meters.txt"

DEFAULT_DEPTH = 32

TYPE_LINEAR = "linear"
TYPE_METALINEAR = "metalinear"
TYPE_CIRCULAR = "circular"
TYPE_METACIRCULAR = "metacircular"
TYPE_METACASSETE = "metacassete"
TYPE_METACASSETEWITHSPECTRUM="metacassetewithspectrum"
TYPE_METACASSETECIRCLEWITHSPECTRUM="metacassetecirclewithspectrum"
TYPE_METACASSETECIRCLE = "metacassetecircle"
TYPE_METALINEARSPECTRUM = "metalinearspectrum"
TYPE_METACIRCLESSPECTRUM = "metacirclespectrum"
TYPE_TUNERCIRCLESSPECTRUM = "tunercirclespectrum"
WEB_SERVER = "web.server"
HTTP_PORT = "http.port"

NEEDLE_WIDTH = "needle.width"
NEEDLE_HEIGHT = "needle.height"
LEFT_START_ANGLE = "left.start.angle"
LEFT_STOP_ANGLE = "left.stop.angle"
RIGHT_START_ANGLE = "right.start.angle"
RIGHT_STOP_ANGLE = "right.stop.angle"
LEFT_NEEDLE_FLIP = "left.needle.flip"
RIGHT_NEEDLE_FLIP = "right.needle.flip"

DIRECTION_LEFT_RIGHT = "left-right"
DIRECTION_BOTTOM_TOP = "bottom-top"
DIRECTION_TOP_BOTTOM = "top-bottom"
DIRECTION_EDGES_CENTER = "edges-center"
DIRECTION_CENTER_EDGES = "center-edges"

INDICATOR_TYPE = "indicator.type"
SINGLE = "single"

class ConfigFileParser(object):
    """ Configuration file parser """
    
    def __init__(self):
        """ Initializer """  
              
        self.meter_config = {}
        c = ConfigParser()

        config_path = "."
        if __package__:
            pkg_parts = __package__.split(".")
            if len(pkg_parts) > 0:
                config_path = os.path.join(os.getcwd(), "screensaver", self.name)
        
        config_file_path = os.path.join(config_path, FILE_CONFIG)
        c.read(config_file_path)

        if c.get(CURRENT, BASE_FOLDER):
            config_path = c.get(CURRENT, BASE_FOLDER)
        
        self.meter_config[METER] = c.get(CURRENT, METER)
        self.meter_config["meter.list"] = c.get(CURRENT, "meter.list")
        self.meter_config["metadatasourcedns"] = c.get(CURRENT,"metadatasourcedns")
        self.meter_config["dsdaddfactor"] = c.getfloat(CURRENT, "dsdaddfactor")
        self.meter_config[RANDOM_METER_INTERVAL] = c.getint(CURRENT, RANDOM_METER_INTERVAL)
        self.meter_config[EXIT_ON_TOUCH] = c.getboolean(CURRENT, EXIT_ON_TOUCH)
        self.meter_config[STOP_DISPLAY_ON_TOUCH] = c.getboolean(CURRENT, STOP_DISPLAY_ON_TOUCH)
        self.meter_config[OUTPUT_DISPLAY] = c.getboolean(CURRENT, OUTPUT_DISPLAY)
        self.meter_config[OUTPUT_SERIAL] = c.getboolean(CURRENT, OUTPUT_SERIAL)
        self.meter_config[OUTPUT_I2C] = c.getboolean(CURRENT, OUTPUT_I2C)
        self.meter_config[OUTPUT_PWM] = c.getboolean(CURRENT, OUTPUT_PWM)
        self.meter_config[OUTPUT_HTTP] = c.getboolean(CURRENT, OUTPUT_HTTP)
        self.meter_config[USE_LOGGING] = c.getboolean(CURRENT, USE_LOGGING)
        self.meter_config['use.loglevel'] = c.get(CURRENT, 'use.loglevel')
        self.meter_config[USE_CACHE] = c.getboolean(CURRENT, USE_CACHE)
        self.meter_config[FRAME_RATE] = c.getint(CURRENT, FRAME_RATE)
        
        self.meter_config[SERIAL_INTERFACE] = {}
        self.meter_config[SERIAL_INTERFACE][DEVICE_NAME] = c.get(SERIAL_INTERFACE, DEVICE_NAME)
        self.meter_config[SERIAL_INTERFACE][BAUD_RATE] = c.getint(SERIAL_INTERFACE, BAUD_RATE)
        self.meter_config[SERIAL_INTERFACE][INCLUDE_TIME] = c.getboolean(SERIAL_INTERFACE, INCLUDE_TIME)
        self.meter_config[SERIAL_INTERFACE][UPDATE_PERIOD] = c.getfloat(SERIAL_INTERFACE, UPDATE_PERIOD)
        
        self.meter_config[I2C_INTERFACE] = {}
        self.meter_config[I2C_INTERFACE][PORT] = c.getint(I2C_INTERFACE, PORT)
        self.meter_config[I2C_INTERFACE][LEFT_CHANNEL_ADDRESS] = int(c.get(I2C_INTERFACE, LEFT_CHANNEL_ADDRESS), 0)
        self.meter_config[I2C_INTERFACE][RIGHT_CHANNEL_ADDRESS] = int(c.get(I2C_INTERFACE, RIGHT_CHANNEL_ADDRESS), 0)
        self.meter_config[I2C_INTERFACE][OUTPUT_SIZE] = c.getint(I2C_INTERFACE, OUTPUT_SIZE)
        self.meter_config[I2C_INTERFACE][UPDATE_PERIOD] = c.getfloat(I2C_INTERFACE, UPDATE_PERIOD)
        
        self.meter_config[PWM_INTERFACE] = {}
        self.meter_config[PWM_INTERFACE][FREQUENCY] = c.getint(PWM_INTERFACE, FREQUENCY)
        self.meter_config[PWM_INTERFACE][GPIO_PIN_LEFT] = c.getint(PWM_INTERFACE, GPIO_PIN_LEFT)
        self.meter_config[PWM_INTERFACE][GPIO_PIN_RIGHT] = c.getint(PWM_INTERFACE, GPIO_PIN_RIGHT)
        self.meter_config[PWM_INTERFACE][UPDATE_PERIOD] = c.getfloat(PWM_INTERFACE, UPDATE_PERIOD)

        self.meter_config[HTTP_INTERFACE] = {TARGET_URL: c.get(HTTP_INTERFACE, TARGET_URL)}
        self.meter_config[HTTP_INTERFACE][UPDATE_PERIOD] = c.getfloat(HTTP_INTERFACE, UPDATE_PERIOD)

        self.meter_config[HTTP_PORT] = c.get(WEB_SERVER, HTTP_PORT)

        self.meter_config[SDL_ENV] = self.get_sdl_environment_section(c, SDL_ENV)

        meter_folder = c.get(CURRENT, METER_FOLDER)
        if not meter_folder or not meter_folder[0].isdigit():
            print("Invalid meter folder name: " + meter_folder)
            os._exit(0)

        self.meter_config[SCREEN_INFO] = {}
        self.meter_config[SCREEN_INFO][METER_FOLDER] = meter_folder
        self.meter_config[SCREEN_INFO][WIDTH], self.meter_config[SCREEN_INFO][HEIGHT] = self.get_meter_size(meter_folder)
        self.meter_config[SCREEN_INFO][DEPTH] = DEFAULT_DEPTH
        self.meter_config[DATA_SOURCE] = self.get_data_source_section(c, DATA_SOURCE)        

        try:
            self.meter_config[SCREEN_INFO][WIDTH] = c.getint(CURRENT, SCREEN_WIDTH)
            self.meter_config[SCREEN_INFO][HEIGHT] = c.getint(CURRENT, SCREEN_HEIGHT)
        except:
            pass
        
        meter_config_path = os.path.join(config_path, meter_folder, FILE_METER_CONFIG)
        if not os.path.exists(meter_config_path):
            print("Cannot read file: " + meter_config_path)
            os._exit(0)

        c = ConfigParser()
        c.read(meter_config_path)
        available_meter_names = list()
        
        for section in c.sections():
            available_meter_names.append(section)
            meter_type = c.get(section, METER_TYPE)
            if meter_type == TYPE_LINEAR:
                self.meter_config[section] = self.get_linear_section(c, section, meter_type)
            elif meter_type == TYPE_CIRCULAR:
                self.meter_config[section] = self.get_circular_section(c, section, meter_type)
            elif meter_type == TYPE_METACIRCULAR:
                self.meter_config[section] = self.get_metacircular_section(c, section, meter_type)
            elif meter_type == TYPE_METALINEAR:
                self.meter_config[section] = self.get_matalinear_section(c, section, meter_type)
            elif meter_type == TYPE_METALINEARSPECTRUM:
                self.meter_config[section] = self.get_matalinearspectrum_section(c, section, meter_type)
            elif meter_type == TYPE_METACIRCLESSPECTRUM or meter_type == TYPE_TUNERCIRCLESSPECTRUM:
                self.meter_config[section] = self.get_matacirclesspectrum_section(c, section, meter_type)
            elif meter_type == TYPE_METACASSETE:
                self.meter_config[section] = self.get_cassete_section(c, section, meter_type)
            elif meter_type  ==TYPE_METACASSETEWITHSPECTRUM:
                self.meter_config[section] = self.get_cassetewithspectrum_section(c, section, meter_type)
            elif meter_type == TYPE_METACASSETECIRCLEWITHSPECTRUM:
                self.meter_config[section] = self.get_cassetecirclewithspectrum_section(c, section, meter_type)

            elif meter_type == TYPE_METACASSETECIRCLE:
                self.meter_config[section] = self.get_cassetecircle_section(c, section, meter_type)
        if "," in self.meter_config[METER]:
            names = self.meter_config[METER].split(",")
            available_meter_names = list(map(str.strip, names))

        self.meter_config[METER_NAMES] = available_meter_names
        self.meter_config[BASE_PATH] = config_path
    
    def get_meter_size(self, meter_folder):
        """ Get meter size from the meter folder name using convention:
        480x320-any_text, where 480-meter width, 320-meter height, followed by arbitrary text
        
        :param meter_folder: meter folder in above-mentioned convention

        :return: meter size tuple (width, height)
        """
        w = h = ""
        width_complete = False

        for c in meter_folder:
            if c.isdigit() and not width_complete:
                w += c
            elif c == "x":
                width_complete = True
            elif c.isdigit() and width_complete:
                h += c
            else:
                break

        return (int(w), int(h))

    def get_data_source_section(self, config_file, section):
        """ Parser for data source section
        
        :param config_file: configuration file
        :param section: section name
        """
        d = {}
        d[TYPE] = config_file.get(section, TYPE)
        d[POLLING_INTERVAL] = config_file.getfloat(section, POLLING_INTERVAL)
        d[PIPE_NAME] = config_file.get(section, PIPE_NAME)
        d[VOLUME_CONSTANT] = config_file.getfloat(section, VOLUME_CONSTANT)
        d[VOLUME_MIN] = config_file.getfloat(section, VOLUME_MIN)
        d[VOLUME_MAX] = config_file.getfloat(section, VOLUME_MAX)
        d[VOLUME_MAX_IN_PIPE] = config_file.getfloat(section, VOLUME_MAX_IN_PIPE)
        d[MONO_ALGORITHM] = config_file.get(section, MONO_ALGORITHM)
        d[STEREO_ALGORITHM] = config_file.get(section, STEREO_ALGORITHM)
        d[STEP] = config_file.getint(section, STEP)
        d[SMOOTH_BUFFER_SIZE] = config_file.getint(section, SMOOTH_BUFFER_SIZE)
        return d

    def get_mata_section(self, config_file, section, d):
        d['progressbar.width'] = config_file.getint(section, 'progressbar.width')
        d['progressbar.height'] = config_file.getint(section, 'progressbar.height')
        d['progressbar.corner_radius'] = config_file.getint(section, 'progressbar.corner_radius')
        d['progressbar.x'] = config_file.getint(section, 'progressbar.x')
        d['progressbar.y'] = config_file.getint(section, 'progressbar.y')
        d['progressbar.bar_color'] = make_tuple(config_file.get(section, 'progressbar.bar_color'))
        d['progressbar.background_color'] = make_tuple(config_file.get(section, 'progressbar.background_color'))
        d['metatext.bigfontsize'] = config_file.getint(section, 'metatext.bigfontsize')
        d['metatext.smallfontsize'] = config_file.getint(section, 'metatext.smallfontsize')
        d['metatext.tinyfontsize'] = config_file.getint(section, 'metatext.tinyfontsize')
        d['metatext.bitratefont'] = config_file.get(section, 'metatext.bitratefont')
        d['metatext.durfontsize'] = config_file.getint(section, 'metatext.durfontsize')
        d['metatext.textcolor'] = make_tuple(config_file.get(section, 'metatext.textcolor'))
        d['metatext.title'] = make_tuple(config_file.get(section, 'metatext.title'))
        d['metatext.album'] = make_tuple(config_file.get(section, 'metatext.album'))
        d['metatext.artist'] = make_tuple(config_file.get(section, 'metatext.artist'))
        d['metatext.trimtitle'] = config_file.getint(section, 'metatext.trimtitle')
        d['metatext.trimalbum'] = config_file.getint(section, 'metatext.trimalbum')
        d['metatext.trimartist'] = config_file.getint(section, 'metatext.trimartist')
        d['metatext.bitrate'] = make_tuple(config_file.get(section, 'metatext.bitrate'))
        d['metatext.duration'] = make_tuple(config_file.get(section, 'metatext.duration'))
        d['metatext.osversion'] = make_tuple(config_file.get(section, 'metatext.osversion'))
        d['metatext.iscenter'] = config_file.getboolean(section, 'metatext.iscenter')
        d['metatext.fontcolor'] = make_tuple(config_file.get(section, 'metatext.fontcolor'))
        d['icons.usepeak'] = config_file.getboolean(section, 'icons.usepeak')
        d['icons.usesingle'] = config_file.getboolean(section, 'icons.usesingle')
        d['icons.peakthreshold'] = config_file.getint(section, 'icons.peakthreshold')
        d['cover.size'] = config_file.getint(section, 'cover.size')
        d['cover.position'] = make_tuple(config_file.get(section, 'cover.position'))
        d['icons.eth.position'] = make_tuple(config_file.get(section, 'icons.eth.position'))
        d['icons.wifi.position'] = make_tuple(config_file.get(section, 'icons.wifi.position'))
        d['icons.inet.position'] = make_tuple(config_file.get(section, 'icons.inet.position'))
        d['icons.rnd.position'] = make_tuple(config_file.get(section, 'icons.rnd.position'))
        d['icons.rpt.position'] = make_tuple(config_file.get(section, 'icons.rpt.position'))
        d['icons.play.position'] = make_tuple(config_file.get(section, 'icons.play.position'))
        d['icons.redledleft.position'] = make_tuple(config_file.get(section, 'icons.redledleft.position'))
        d['icons.redledright.position'] = make_tuple(config_file.get(section, 'icons.redledright.position'))
        d['icons.airplay_emulation.position'] = make_tuple(config_file.get(section, 'icons.airplay_emulation.position'))
        d['icons.tidalconnect.position'] = make_tuple(config_file.get(section, 'icons.tidalconnect.position'))
        d['icons.mpd.position'] = make_tuple(config_file.get(section, 'icons.mpd.position'))
        d['icons.volumio.position'] = make_tuple(config_file.get(section, 'icons.volumio.position'))
        d['icons.tidal.position'] = make_tuple(config_file.get(section, 'icons.tidal.position'))
        d['icons.aac.position'] = make_tuple(config_file.get(section, 'icons.aac.position'))
        d['icons.mqa.position'] = make_tuple(config_file.get(section, 'icons.mqa.position'))
        d['icons.flac.position'] = make_tuple(config_file.get(section, 'icons.flac.position'))
        d['icons.dsf.position'] = make_tuple(config_file.get(section, 'icons.dsf.position'))
        d['icons.mp3.position'] = make_tuple(config_file.get(section, 'icons.mp3.position'))
        d['icons.color'] = config_file.get(section, 'icons.color')
        d['knobs.selectmeterfrom'] = make_tuple(config_file.get(section, 'knobs.selectmeterfrom'))
        d['knobs.selectmeterto'] = make_tuple(config_file.get(section, 'knobs.selectmeterto'))
        d['knobs.powerfrom'] = make_tuple(config_file.get(section, 'knobs.powerfrom'))
        d['knobs.powerto'] = make_tuple(config_file.get(section, 'knobs.powerto'))
        d['metatext.fontname'] = config_file.get(section, 'metatext.fontname')
        d['metatext.bitratefontsize'] = config_file.getint(section, 'metatext.bitratefontsize')
        d['metatext.smallHebfontname'] = config_file.get(section, 'metatext.smallHebfontname')
        d['metatext.bigHebfontname'] = config_file.get(section, 'metatext.bigHebfontname')
    def get_matalinear_section(self, config_file, section, meter_type):
        d=self.get_linear_section(config_file, section, meter_type)
        self.get_mata_section(config_file, section, d)
        return d
    def get_matalinearspectrum_section(self ,config_file, section, meter_type):
        d=self.get_matalinear_section(config_file, section, meter_type)
        d['spectrum.type'] = config_file.get(section, 'spectrum.type')
        return d
    def get_matacirclesspectrum_section(self ,config_file, section, meter_type):
        d=self.get_metacircular_section(config_file, section, meter_type)
        d['spectrum.type'] = config_file.get(section, 'spectrum.type')
        return d
#
    def get_metacircular_section(self, config_file, section, meter_type):
        d = self.get_circular_section( config_file, section, meter_type)
        self.get_mata_section(config_file, section,  d)
        return d
    def get_cassete_section(self, config_file, section, meter_type):
        d = self.get_matalinear_section(config_file, section, meter_type)
        d['icons.casstewheel'] = config_file.get(section, 'icons.casstewheel')
        d['icons.casseteclear'] = config_file.get(section, 'icons.casseteclear')
        d['icons.casstewheelleft.position'] = make_tuple(config_file.get(section, 'icons.casstewheelleft.position'))
        d['icons.casstewheelright.position'] = make_tuple(config_file.get(section, 'icons.casstewheelright.position'))
        d['icons.casseteclear.position'] = make_tuple(config_file.get(section, 'icons.casseteclear.position'))
        d['icons.casseteclear.width'] = config_file.getint(section, 'icons.casseteclear.width')

        return d
    def get_cassetewithspectrum_section(self, config_file, section, meter_type):
        d = self.get_cassete_section(config_file, section, meter_type)
        d['spectrum.type'] = config_file.get(section, 'spectrum.type')
        return d

    def get_cassetecirclewithspectrum_section(self, config_file, section, meter_type):
        d = self.get_cassetecircle_section(config_file, section, meter_type)
        d['spectrum.type'] = config_file.get(section, 'spectrum.type')
        return d
#
    def get_cassetecircle_section(self, config_file, section, meter_type):
        d = self.get_metacircular_section(config_file, section, meter_type)
        d['icons.casstewheel'] = config_file.get(section, 'icons.casstewheel')
        d['icons.casseteclear'] = config_file.get(section, 'icons.casseteclear')
        d['icons.casstewheelleft.position'] = make_tuple(config_file.get(section, 'icons.casstewheelleft.position'))
        d['icons.casstewheelright.position'] = make_tuple(config_file.get(section, 'icons.casstewheelright.position'))
        d['icons.casseteclear.position'] = make_tuple(config_file.get(section, 'icons.casseteclear.position'))
        d['icons.casseteclear.width'] = config_file.getint(section, 'icons.casseteclear.width')

        return d

    def get_linear_section(self, config_file, section, meter_type):
        """ Parser for linear meter
        
        :param config_file: configuration file
        :param section: section name
        :param meter_type: type of the meter
        """
        d = {}
        self.get_common_options(d, config_file, section, meter_type)
        d[LEFT_X] = config_file.getint(section, LEFT_X)
        d[LEFT_Y] = config_file.getint(section, LEFT_Y)
        d[RIGHT_X] = config_file.getint(section, RIGHT_X)
        d[RIGHT_Y] = config_file.getint(section, RIGHT_Y)
        d[POSITION_REGULAR] = config_file.getint(section, POSITION_REGULAR)
        d[STEP_WIDTH_REGULAR] = config_file.getint(section, STEP_WIDTH_REGULAR)
        d[METER_X] = config_file[section].getint(METER_X, 0)
        d[METER_Y] = config_file[section].getint(METER_Y, 0)
        d[SCREEN_BGR] = config_file.get(section, SCREEN_BGR)
        d[POSITION_OVERLOAD] = config_file[section].getint(POSITION_OVERLOAD, 0)
        d[STEP_WIDTH_OVERLOAD] = config_file[section].getint(STEP_WIDTH_OVERLOAD, 0)
        d[DIRECTION] = config_file[section].get(DIRECTION, None)
        d[INDICATOR_TYPE] = config_file[section].get(INDICATOR_TYPE, None)
        d[FLIP_LEFT_X] = config_file[section].get(FLIP_LEFT_X, None)
        d[FLIP_RIGHT_X] = config_file[section].get(FLIP_RIGHT_X, None)

        return d

    def get_circular_section(self, config_file, section, meter_type):
        """ Parser for circular meter
        
        :param config_file: configuration file
        :param section: section name
        :param meter_type: type of the meter
        """
        d = {}
        self.get_common_options(d, config_file, section, meter_type)
        d[STEPS_PER_DEGREE] = config_file.getint(section, STEPS_PER_DEGREE)
        d[START_ANGLE] = config_file[section].getint(START_ANGLE, None)
        d[STOP_ANGLE] = config_file[section].getint(STOP_ANGLE, None)

        d[LEFT_START_ANGLE] = config_file[section].getint(LEFT_START_ANGLE, d[START_ANGLE])
        d[LEFT_STOP_ANGLE] = config_file[section].getint(LEFT_STOP_ANGLE, d[STOP_ANGLE])
        d[RIGHT_START_ANGLE] = config_file[section].getint(RIGHT_START_ANGLE, d[START_ANGLE])
        d[RIGHT_STOP_ANGLE] = config_file[section].getint(RIGHT_STOP_ANGLE, d[STOP_ANGLE])

        d[LEFT_NEEDLE_FLIP] = config_file[section].getboolean(LEFT_NEEDLE_FLIP, False)
        d[RIGHT_NEEDLE_FLIP] = config_file[section].getboolean(RIGHT_NEEDLE_FLIP, False)

        d[DISTANCE] = config_file.getint(section, DISTANCE)
        d[METER_X] = config_file[section].getint(METER_X, 0)
        d[METER_Y] = config_file[section].getint(METER_Y, 0)
        d[SCREEN_BGR] = config_file.get(section, SCREEN_BGR)

        if d[CHANNELS] == 1:                  
            d[MONO_ORIGIN_X] = config_file.getint(section, MONO_ORIGIN_X)
            d[MONO_ORIGIN_Y] = config_file.getint(section, MONO_ORIGIN_Y)            
        else:            
            d[LEFT_ORIGIN_X] = config_file.getint(section, LEFT_ORIGIN_X)
            d[LEFT_ORIGIN_Y] = config_file.getint(section, LEFT_ORIGIN_Y)            
            d[RIGHT_ORIGIN_X] = config_file.getint(section, RIGHT_ORIGIN_X)
            d[RIGHT_ORIGIN_Y] = config_file.getint(section, RIGHT_ORIGIN_Y)

        return d
        
    def get_common_options(self, d, config_file, section, meter_type):
        """ Parser for the common section of the configuration file
        
        :param d: common section dictionary
        :param config_file: configuration file
        :param section: section name
        :param meter_type: type of the meter
        """
        d[METER_TYPE] = meter_type
        d[CHANNELS] = config_file.getint(section, CHANNELS)
        d[UI_REFRESH_PERIOD] = config_file.getfloat(section, UI_REFRESH_PERIOD)                
        d[BGR_FILENAME] = config_file.get(section, BGR_FILENAME)
        d[FGR_FILENAME] = config_file[section].get(FGR_FILENAME, None)
        d[INDICATOR_FILENAME] = config_file.get(section, INDICATOR_FILENAME)

    def get_sdl_environment_section(self, config_file, section):
        """ Parser for SDL library OS environment section

        :param config_file: configuration file
        :param section: section name
        """
        d = {}
        d[FRAMEBUFFER_DEVICE] = config_file.get(section, FRAMEBUFFER_DEVICE)
        d[MOUSE_DEVICE] = config_file.get(section, MOUSE_DEVICE)
        d[MOUSE_DRIVER] = config_file.get(section, MOUSE_DRIVER)
        d[MOUSE_ENABLED] = config_file.getboolean(section, MOUSE_ENABLED)
        d[VIDEO_DRIVER] = config_file.get(section, VIDEO_DRIVER)
        d[VIDEO_DISPLAY] = config_file.get(section, VIDEO_DISPLAY)
        d[DOUBLE_BUFFER] = config_file.getboolean(section, DOUBLE_BUFFER)
        d[NO_FRAME] = config_file.getboolean(section, NO_FRAME)
        return d
