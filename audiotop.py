#! /usr/bin/python3
import sys
from subprocess import Popen
import os
import time
from datetime import datetime
import signal
import psutil
import socketio
import threading
import settings
sys.stderr = open("audiotop.log","wt")
settings = settings.Settings()
settings.retreive()

def process_status(pid):
    return [ps for ps in psutil.process_iter(['pid', 'name']) if ps.pid == pid and ps.status() != 'zombie']


def volumiostatus():
    return "play";

def shutdown(sigid,name):
    global running
    print("bye",sigid,name)
    running=False

def closepeppy():
    global peppy
    if peppy:
        os.kill(peppy.pid, signal.SIGUSR1)
        peppy.wait()
        peppy = None


sio = socketio.Client()
@sio.on('pushState')
def on_message(data):
    global info, isupdateinfo
    info = data
def startsockio():
    sio.connect(f"http://{settings['config_metadata_url']['value']}:3000")
    sio.emit('getState', {})
    sio.wait()



TIMETOSLEEP =  settings['config_sleep_timer']['value']
peppy = None
running = True
info={}
sockectworker = threading.Thread(target=startsockio)
sockectworker.start()
signal.signal(signal.SIGUSR1, shutdown)
os.chdir("/data/plugins/user_interface/audiotop/PeppyMeter")
lasttime = datetime.now()

while running:
    try:
        #sio.emit('getState', {})
        if 'status' in info and info['status'] == "play":
            if not peppy or not process_status(peppy.pid):
                #peppy = Popen(["../vvenv/bin/python", "peppymeter.py"])
                peppy = Popen(["./peppymeter.py"])
            lasttime = datetime.now()
        else:
            if TIMETOSLEEP>0 and (datetime.now() - lasttime).total_seconds() > TIMETOSLEEP:
                closepeppy()

        time.sleep(2)
        #print(info)
    except Exception  as ex:
        time.sleep(5)
        print(ex,file=sys.stderr)

else:
    sio.disconnect()
    closepeppy()

