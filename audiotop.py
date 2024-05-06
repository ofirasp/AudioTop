#! /usr/bin/python3
import subprocess
import sys
from subprocess import Popen
import os
import time
from datetime import datetime
import signal
import socketio
from PeppyMeter import settings

basedir = '/data/plugins/user_interface/audiotop' if "linux" in sys.platform else '.'
sys.stderr = open(basedir+"/audiotop.log","at")
print(f"Starting audiotop {datetime.now()}",file=sys.stderr,flush=True)

peppy = None
running = True
info={}
settings = settings.Settings()
settings.retreive()
TIMETOSLEEP =  settings['config_sleep_timer']['value']
TIMETOSPING = 15
RETRIES = 5

def peppyisalive(sigpid,name):
    global alivelasttime
    alivelasttime = datetime.now()

def checkpeppylive():
    global alivelasttime
    if (datetime.now() - alivelasttime).total_seconds() > TIMETOSPING:
        print(f"Peppy is hang, shut it down {datetime.now()}",file=sys.stderr,flush=True)
        alivelasttime = datetime.now()
        closepeppy()

def shutdown(sigid,name):
    global running
    print(f"Shutting down audiotop {datetime.now()}",sigid,name,file=sys.stderr,flush=True)
    running=False

def closepeppy():
    global peppy
    if peppy:
        peppy.send_signal(signal.SIGUSR1)
        #os.kill(peppy.pid, signal.SIGUSR1)
        try:
            peppy.wait(timeout=TIMETOSPING)
            print(f"stopping peppymeter {datetime.now()}", file=sys.stderr, flush=True)
        except:
            try:
                peppy.send_signal(signal.SIGKILL)
                #os.kill(peppy.pid, signal.SIGKILL)
                peppy.wait(timeout=TIMETOSPING)
                print(f"killing peppymeter {datetime.now()}", file=sys.stderr, flush=True)
            except:
                print(f"error on killing peppymeter {datetime.now()}", file=sys.stderr, flush=True)
        peppy = None

sio = socketio.Client()
@sio.on('pushState')
def on_message(data):
    global info, isupdateinfo
    info = data
def startsockio():
    trycount = 0
    while trycount< RETRIES:
        try:
            sio.connect(f"http://{settings['config_metadata_url']['value']}:3000")
            sio.emit('getState', {})
            print("Listening...", file=sys.stderr, flush=True)
            break
        except Exception as ex:
            trycount+=1
            time.sleep(0.5)
            print(f"error on starting socketio {datetime.now()} ex:{ex}", file=sys.stderr, flush=True)
    else:
        print(f"error on starting socketio, exceeded max retries exit plugin", file=sys.stderr, flush=True)
        exit(1)

signal.signal(signal.SIGUSR1, shutdown)
signal.signal(signal.SIGINFO, peppyisalive)

os.chdir(basedir+"/PeppyMeter")

lasttime = datetime.now()
alivelasttime = lasttime

startsockio()
while running:
    try:
        if 'status' in info and info['status'] == "play":
            if not peppy or peppy.poll() != None:
                peppy = Popen(["../vvenv/bin/python", "peppymeter.py"],stdin=subprocess.PIPE)
                peppy.stdin.write(f"{os.getpid()}\n".encode())
                peppy.stdin.close()
            lasttime = datetime.now()
        else:
            if TIMETOSLEEP>0 and (datetime.now() - lasttime).total_seconds() > TIMETOSLEEP:
                closepeppy()
        time.sleep(2)
        checkpeppylive()
    except Exception  as ex:
        time.sleep(5)
        print(ex,file=sys.stderr,flush=True)
else:
    sio.disconnect()
    closepeppy()

print(f"Stopping audiotop {datetime.now()}",file=sys.stderr,flush=True)