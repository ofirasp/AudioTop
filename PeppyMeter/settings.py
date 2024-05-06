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
        elif (os.path.isfile('../config.json')):
            settings_file = open('../config.json')
        elif (os.path.isfile('./config.json')):
            settings_file = open('./config.json')
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
            try:
                self.settings['config_sleep_timer']['value'] = int(self.settings['config_sleep_timer']['value'])
            except:
                self.settings['config_sleep_timer']['value']=30
            try:
                self.settings['config_metadata_url']['value'] = self.settings['config_metadata_url']['value']
            except:
                self.settings['config_metadata_url']['value']="127.0.0.1"
            try:
                self.settings['config_switch_meter_on_title']['value'] = self.settings['config_switch_meter_on_title']['value']
            except:
                self.settings['config_switch_meter_on_title']['value'] = False
            try:
                self.settings['config_switch_meter_on_album']['value'] = self.settings['config_switch_meter_on_album']['value']
            except:
                self.settings['config_switch_meter_on_album']['value'] = False
            try:
                self.settings['config_switch_meter_on_restart']['value'] = self.settings['config_switch_meter_on_restart']['value']
            except:
                self.settings['config_switch_meter_on_restart']['value'] = False

            return self.settings
        else:
            return False