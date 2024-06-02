# Copyright 2016-2024 Peppy Player peppy.player@gmail.com
#
# This file is part of Peppy Player.
#
# Peppy Player is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Peppy Player is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Peppy Player. If not, see <http://www.gnu.org/licenses/>.

import pygame
import time

class Component(object):
    """ Represent the lowest UI component level.
    This is the only class which knows how to draw on Pygame Screen.
    """

    def __init__(self, util, c=None, x=0, y=0, bb=None, fgr=(0, 0, 0), bgr=(0, 0, 0), v=True):
        """ Initializer

        :param util: utility object
        :param c: component content
        :param x: component coordinate X on Pygame Screen
        :param y: component coordinate Y on Pygame Screen
        :param bb: component bounding box
        :param fgr: component foreground
        :param bgr: component background
        :param v: visibility flag, True - visible, False - invisible
        """
        self.screen = None
        self.screen = util.PYGAME_SCREEN
        self.content = c
        self.content_x = x
        self.content_y = y
        if bb:
            self.bounding_box = pygame.Rect(bb.x, bb.y, bb.w, bb.h)
        else:
            self.bounding_box = None
        self.fgr = fgr
        self.bgr = bgr
        self.visible = v
        self.text = None
        self.text_size = None
        self.image_filename = None


    def clean(self):
        """ Clean component by filling its bounding box by background color """

        if not self.visible: return
        self.draw_rect( f=(0,0,0),r=self.bounding_box)

    def draw(self):
        """ Dispatcher drawing method.
        Distinguishes between Rectangle and Image components.
        Doesn't draw invisible component.
        """
        if not self.visible: return

        if isinstance(self.content, pygame.Rect):
            self.draw_rect(f=(0,0,0), r=self.content)
        else:
            self.draw_image(self.content, self.content_x, self.content_y)

    def draw_rect(self, f, r, t=0):
        """ Draw Rectangle on Pygame Screen

        :param f: outline color
        :param r: rectangle object
        :param t: outline thickness
        """
        if not self.visible: return
        if self.screen:
            pygame.draw.rect(self.screen, f, r, t)

    def draw_image(self, c, x, y):
        """ Draw Image on Pygame Screen

        :param c: image
        :param x: coordinate X of the image top-left corner on Pygame Screen
        :param y: coordinate Y of the image top-left corner on Pygame Screen
        """
        comp = c
        if isinstance(c, tuple):
            comp = c[1]
        if comp and self.screen:
            try:
                if self.bounding_box:
                    if isinstance(self.content, tuple):
                        self.screen.blit(self.content[1], (self.content_x, self.content_y), self.bounding_box)
                    else:
                        self.screen.blit(self.content, self.bounding_box)
                else:
                    self.screen.blit(comp, (x, y))
            except:
                pass

    def set_visible(self, flag):
        """ Set component visibility

        :param flag: True - component visible, False - component invisible
        """
        self.visible = flag

    def refresh(self):
        """ Refresh component. Used for periodical updates  animation. """

        pass


class TextComponent(Component):
    def __init__(self, util, c=None, x=0, y=0, bb=None, fgr=(0, 0, 0), bgr=(0, 0, 0), v=True):
        super().__init__(util, c, x, y, bb, fgr, bgr, v)
        pygame.font.init()  # you have to call this at the start,
        self.config = util.meter_config[util.meter_config['meter']]
        self.artist = '---'
        self.album = '---'
        self.title = '---'
        self.bitrate  = '---'
        self.seek = 0
        self.duration = 0
        self.osversion = '---'
        self.fontcolor =  self.config['metatext.fontcolor']
        self.textcolor = self.config['metatext.textcolor']
        self.bigfont = pygame.font.Font('fonts/'+self.config['metatext.fontname'],self.config['metatext.bigfontsize'])
        self.smallfont = pygame.font.Font('fonts/'+self.config['metatext.fontname'], self.config['metatext.smallfontsize'])
        self.tinyfont = pygame.font.Font('fonts/'+self.config['metatext.fontname'], self.config['metatext.tinyfontsize'])
        self.bitratefont = pygame.font.Font('fonts/'+self.config['metatext.bitratefont'], self.config['metatext.bitratefontsize'])
        self.smallhebfont = pygame.font.Font('fonts/'+self.config['metatext.smallHebfontname'], self.config['metatext.smallfontsize'])
        self.bighebfont = pygame.font.Font('fonts/'+self.config['metatext.bigHebfontname'], self.config['metatext.bigfontsize'])

        self.durfont = pygame.font.Font('fonts/digital-7 (mono).ttf', self.config['metatext.durfontsize'])
        self.clockstart = 0
        self.iscenter = self.config['metatext.iscenter']
    def drawDynamicText(self,text,fonts,trimval,size,color):
        font = fonts[1] if self.hasHeb(text) else fonts[0]
        textsurface = font.render(self.pyHebText(text)[:trimval], True,color )
        textsurface.set_colorkey((0, 0, 0))
        r = textsurface.get_rect(center=size) if  self.iscenter else size
        self.screen.blit(textsurface,r)
    def drawText(self,text,font,size,color):
        textsurface = font.render(text, True, color)
        textsurface.set_colorkey((0, 0, 0))
        self.screen.blit(textsurface, textsurface.get_rect(center=size))

    def draw(self):
        self.drawDynamicText(self.title,(self.bigfont, self.bighebfont),  self.config['metatext.trimtitle'],self.config['metatext.title'],self.fontcolor)
        self.drawDynamicText(self.artist,(self.bigfont, self.bighebfont),  self.config['metatext.trimartist'],self.config['metatext.artist'],self.fontcolor)
        self.drawDynamicText( self.album,(self.smallfont, self.smallhebfont), self.config['metatext.trimalbum'],self.config['metatext.album'],self.fontcolor)
        self.drawText(self.bitrate,self.bitratefont,self.config['metatext.bitrate'],self.textcolor)
        t = self.getSeekTime()
        self.drawText(f"{t[0]} - {t[1]}",self.durfont,  self.config['metatext.duration'],self.textcolor)
        self.drawText(f"OS Version: {self.osversion}",self.tinyfont,  self.config['metatext.osversion'],self.textcolor)

    def getSeekTime(self):
        m =0
        s=0
        dm=0
        ds=0
        if self.seek:
            curtime = float(self.seek / 1000)
            mc, sc = divmod(curtime, 60)
            totaltime = float(self.duration)
            durationm, durations = divmod(totaltime, 60)

            # wt = time.time() - self.clockstart
            # curtime = wt
            mc, sc = divmod(curtime, 60)
            m = int(mc)
            s = int(sc)
            dm = int(durationm)
            ds = int(durations)
            if m * 60 + s >= dm * 60 + ds:
                m = dm
                s = ds
        return (f'{m:2d}:{s:02d}', f'{dm:2d}:{ds:02d}')
    def pyHebText(self,txtString = ''):
        if not type(txtString) is str: return ''
        if any("\u0590" <= c <= "\u05EA" for c in txtString):
            return txtString[::-1]
        return txtString
    def hasHeb(self,txtString):
        if not type(txtString) is str: return False
        return any("\u0590" <= c <= "\u05EA" for c in txtString)

class TextTunerComponent(TextComponent):
    def __init__(self, util, c=None, x=0, y=0, bb=None, fgr=(0, 0, 0), bgr=(0, 0, 0), v=True):
        super().__init__(util,c,x,y,bb,fgr,bgr,v)
        self.durationtextcolor = (255,255,255)
    def draw(self):
        self.drawDynamicText(self.title,(self.bigfont, self.bighebfont),  self.config['metatext.trimtitle'],self.config['metatext.title'],self.fontcolor)
        self.drawDynamicText(self.artist,(self.bigfont, self.bighebfont),  self.config['metatext.trimartist'],self.config['metatext.artist'],self.fontcolor)
        self.drawDynamicText( self.album,(self.smallfont, self.smallhebfont), self.config['metatext.trimalbum'],self.config['metatext.album'],self.fontcolor)

        self.drawText(self.bitrate,self.bitratefont,self.config['metatext.bitrate'],self.fontcolor)

        t = self.getSeekTime()
        self.drawText(f"{t[0]}",self.durfont,  self.config['metatext.duration'],self.durationtextcolor)
        pos = list(self.config['metatext.duration'])
        pos[1]+=60
        self.drawText(f"{t[1]}", self.durfont, pos, self.durationtextcolor)

        self.drawText(f"OS Version: {self.osversion}",self.tinyfont,  self.config['metatext.osversion'],self.textcolor)
class TextNadDeckComponent(TextComponent):
    def __init__(self, util, c=None, x=0, y=0, bb=None, fgr=(0, 0, 0), bgr=(0, 0, 0), v=True):
        super().__init__(util,c,x,y,bb,fgr,bgr,v)
        self.durationtextcolor = (255,255,255)
    def draw(self):
        self.drawDynamicText(self.title,(self.bigfont, self.bighebfont),  self.config['metatext.trimtitle'],self.config['metatext.title'],self.fontcolor)
        self.drawDynamicText(self.artist,(self.bigfont, self.bighebfont),  self.config['metatext.trimartist'],self.config['metatext.artist'],self.fontcolor)
        self.drawDynamicText( self.album,(self.smallfont, self.smallhebfont), self.config['metatext.trimalbum'],self.config['metatext.album'],self.fontcolor)
        self.drawText(self.bitrate,self.bitratefont,self.config['metatext.bitrate'],self.textcolor)
        t = self.getSeekTime()
        self.drawText(f"{t[0]}",self.durfont,  self.config['metatext.duration'],self.durationtextcolor)
        pos = list(self.config['metatext.duration'])
        pos[1] += 47
        self.drawText(f"{t[1]}", self.durfont, pos, self.durationtextcolor)
        self.drawText(f"OS Version: {self.osversion}",self.tinyfont,  self.config['metatext.osversion'],self.textcolor)

class TextAkaiDeckComponent(TextComponent):
    def __init__(self, util, c=None, x=0, y=0, bb=None, fgr=(0, 0, 0), bgr=(0, 0, 0), v=True):
        super().__init__(util,c,x,y,bb,fgr,bgr,v)
        self.durationtextcolor = (255,255,255)
        self.tinyfont = pygame.font.Font('fonts/Arial.ttf', self.config['metatext.tinyfontsize'])
    def draw(self):

        self.drawDynamicText(f"{self.album}:{self.title}",(self.bigfont, self.bighebfont),  self.config['metatext.trimtitle'],self.config['metatext.title'],self.fontcolor)
        self.drawDynamicText(self.artist,(self.bigfont, self.bighebfont),  self.config['metatext.trimartist'],self.config['metatext.artist'],self.fontcolor)
        #self.drawDynamicText( self.album,(self.smallfont, self.smallhebfont), self.config['metatext.trimalbum'],self.config['metatext.album'],self.fontcolor)
        self.drawText(self.bitrate,self.bitratefont,self.config['metatext.bitrate'],self.fontcolor)
        t = self.getSeekTime()
        self.drawText(f"{t[0]}-{t[1]}",self.durfont,  self.config['metatext.duration'],self.fontcolor)
        self.drawText(f"OS Version: {self.osversion}",self.tinyfont,  self.config['metatext.osversion'],self.textcolor)
class TextTeacDeckComponent(TextComponent):
    def draw(self):
        self.drawDynamicText(f"{self.album}:{self.title}", (self.bigfont, self.bighebfont),
                             self.config['metatext.trimtitle'], self.config['metatext.title'], self.fontcolor)
        self.drawDynamicText(self.artist, (self.bigfont, self.bighebfont), self.config['metatext.trimartist'],
                             self.config['metatext.artist'], self.fontcolor)
        # self.drawDynamicText( self.album,(self.smallfont, self.smallhebfont), self.config['metatext.trimalbum'],self.config['metatext.album'],self.fontcolor)
        self.drawText(self.bitrate, self.bitratefont, self.config['metatext.bitrate'], self.fontcolor)
        t = self.getSeekTime()
        pos = self.config['metatext.duration']
        self.drawText(f"{t[0]}", self.durfont, pos, self.fontcolor)
        self.drawText(f"{t[1]}", self.durfont, (pos[0]+140,pos[1]), self.fontcolor)
        self.drawText(f"OS Version: {self.osversion}", self.tinyfont, self.config['metatext.osversion'], self.textcolor)

class ProgressBarComponent(Component):
    def __init__(self, util, c=None, x=0, y=0, bb=None, fgr=(0, 0, 0), bgr=(0, 0, 0), v=True):
        super().__init__(util, c, x, y, bb, fgr, bgr, v)
        m = util.meter_config[util.meter_config['meter']]
        self.width = m['progressbar.width']
        self.height = m['progressbar.height']
        self.bar_color = m['progressbar.bar_color']
        self.background_color = m['progressbar.background_color']
        self.corner_radius = m['progressbar.corner_radius']
        self.y = m['progressbar.y']
        self.x = m['progressbar.x']
        self.progress = 0
    def draw(self):
     try:
         #,border_radius= self.corner_radius   only > python 3.8
        pygame.draw.rect(self.screen, self.background_color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(self.screen, self.bar_color, (self.x, self.y, self.width*(self.progress/100), self.height))
     except Exception as ex:
        pass
class ProgressReelComponent(Component):
    def __init__(self, util,leftcenter,rightcenter,startwidth,radfactor ,c=None, x=0, y=0, bb=None, fgr=(0, 0, 0), bgr=(0, 0, 0), v=True):
        super().__init__(util, c, x, y, bb, fgr, bgr, v)
        self.leftcenter=leftcenter
        self.rightcenter=rightcenter
        self.startwidth=startwidth
        self.radfactor=radfactor
        self.progress = 0
    def draw(self):
     try:
         pygame.draw.circle(self.screen, (0, 0, 0), self.leftcenter,int(self.radfactor*100 * (1 - self.progress / 100) + self.startwidth), 0)
         pygame.draw.circle(self.screen, (0, 0, 0), self.rightcenter,int(self.radfactor*100 * (self.progress / 100) + self.startwidth), 0)
        # pygame.draw.circle(self.screen, (0, 0, 0), (649, 155), int(100 * (1 - self.progress / 100)+40), 0)
        # pygame.draw.circle(self.screen, (0, 0, 0), (1119, 155), int(100 * (self.progress / 100)+40), 0)
     except Exception as ex:
        pass
class TunerProgressBarComponent(ProgressBarComponent):
    def __init__(self, util, c=None, x=0, y=0, bb=None, fgr=(0, 0, 0), bgr=(0, 0, 0), v=True):
        super().__init__(util, c, x, y, bb, fgr, bgr, v)
        m = util.meter_config[util.meter_config['meter']]
        self.width = m['progressbar.width']
        self.height = m['progressbar.height']
        self.bar_color = m['progressbar.bar_color']
        self.background_color = m['progressbar.background_color']
        self.corner_radius = m['progressbar.corner_radius']
        self.y = m['progressbar.y']
        self.x = m['progressbar.x']
        self.progress = 0

    def draw(self):
        try:
            # ,border_radius= self.corner_radius   only > python 3.8
            #pygame.draw.rect(self.screen, self.background_color, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(self.screen, self.bar_color,
                             (self.x, self.y, self.width * (self.progress / 100), self.height))
        except Exception as ex:
            pass