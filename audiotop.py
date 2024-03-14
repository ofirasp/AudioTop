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

def process_status(pid):
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['pid'] == pid:
            status = process.status()
            return status=="running"
    return False

def volumiostatus():
    return "play";

def shutdown():
    global running
    running=False

def closepeppy(peppy):
    if peppy:
        os.kill(peppy.pid, signal.SIGUSR1)
        peppy.wait()


sio = socketio.Client()
@sio.on('pushState')
def on_message(data):
    global info, isupdateinfo
    info = data
def startsockio():
    sio.connect('http://volumio.local:3000')
    sio.emit('getState', {})
    sio.wait()

settings = settings.Settings()
settings.retreive()

TIMETOSLEEP =  settings['config_sleep_timer']['value']
peppy = None
running = True
info={}
sockectworker = threading.Thread(target=startsockio)
sockectworker.start()
signal.signal(signal.SIGUSR1, shutdown)
os.chdir("PeppyMeter")
lasttime = datetime.now()


while running:
    try:
        if 'status' in info and info['status'] == "play":
            if not peppy or not process_status(peppy.pid):
                peppy = Popen(["../vvenv/bin/python", "peppymeter.py"])
            lasttime = datetime.now()
        else:
            if (datetime.now() - lasttime).total_seconds() > TIMETOSLEEP:
                closepeppy(peppy)
                peppy = None
        time.sleep(2)
    except Exception  as ex:
        time.sleep(5)
        print(ex,file=sys.stderr)

else:
    sio.disconnect()
    closepeppy(peppy)

