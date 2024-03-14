import json
import os
import sys

class Settings():
    # constructor
    def __init__(self):
        self.info = ' '
        self.settings = {}

    def retreive(self):
        if(os.path.isfile('/data/configuration/user_interface/audiotop/config.json')):
                settings_file = open('/data/configuration/user_interface/audiotop/config.json')
        elif(os.path.isfile('/data/plugins/user_interface/audiotop/config.json')):
                settings_file = open('/data/plugins/user_interface/audiotop/config.json')
        elif (os.path.isfile('config.json')):
            settings_file = open('config.json')
        else:
                print("No config.json found!\nExiting...",file=sys.stderr)
                exit(1)
        settings_file_content = settings_file.read()
        self.settings = json.loads(settings_file_content)
        return self.validate()
    def __getitem__(self, item):
        return self.settings[item]
    def validate(self):
        if(len(self.settings) > 0):
            if self.settings['config_welcome_message_bool']['value']:
                try:
                    self.settings['config_welcome_message_duration']['value'] = int(self.settings['config_welcome_message_duration']['value'])
                    if(self.settings['config_welcome_message_duration']['value'] < 0):
                        self.settings['config_welcome_message_duration']['value'] = 0
                        self.settings['config_welcome_message_bool']['value'] = False
                    if(len(self.settings['config_welcome_message_string']['value']) > 20):
                        self.settings['config_welcome_message_string']['value'] = self.settings['config_welcome_message_string']['value'][0:20]
                except:
                    self.settings['config_welcome_message_duration']['value'] = 0
                    self.settings['config_welcome_message_bool']['value'] = False
            try:
                self.settings['config_sleep_timer']['value'] = int(self.settings['config_sleep_timer']['value'])
            except:
                self.settings['config_sleep_timer']['value']=30

            return self.settings
        else:
            return False