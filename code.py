#!/usr/bin/env python

import time, board, digitalio, audioio, re
from random import randint
import adafruit_esp32spi.adafruit_esp32spi_requests as requests
from adafruit_pyportal import PyPortal
from analogio import AnalogIn
from secrets import secrets

print("PyPortal METAR System Restarting...")

#### Initialize public variables ####
# Set up where we'll be fetching data from - prelim hard-code
airport_icao = 'kash'
checkwx_metar_url = "https://api.checkwx.com/metar/{0}/decoded".format(airport_icao)
checkwx_metar_api_key = secrets['checkwx_token']
checkwx_header = {'X-API-Key': checkwx_metar_api_key}
# JSON Fields to get from URL
raw_metar_text = ['data',0,'raw_text']
station_id = ['data',0,'icao']
flight_category = ['data',0,'flight_category']
# light sensor
analogin = AnalogIn(board.LIGHT)
# data refresh times (minutes of the hour)
metar_refresh = 15
taf_refresh = 0
# init data state holders
field_data = dict()
last_metar_time = 0
# Display "mode" - defaults to METAR (chosen with left buttons)
display_mode = 'METAR'
# "Scan mode" which rotates through various reports
scan_mode = False
#### END INITIALIZE PUBLIC VARIABLES ####


#### SET FILE LOCATIONS ####
# the current working directory (where this file is)
cwd = ("/"+__file__).rsplit('/', 1)[0]
# Directory containing .wav files
sounddir = (cwd+"/sounds")
# images directory
imagedir = (cwd+"/images")
# Visuals for METAR display
metar_bg = imagedir+"/lcars_pyportal_metar.bmp"
taf_bg = imagedir+"/lcars_pyportal_taf.bmp"
error_bg = imagedir+"/lcars_pyportal_offline.bmp"
metar_font = cwd+"/fonts/Okuda-27.bdf"
#### END SET FILE LOCATIONS ####


#### FUNCTION DEFINITIONS ####

# Play the "command systems offline" sound effect
def play_offline_audio():
    offline = (sounddir+"/offline.wav")
    pyportal.play_file(offline)

# Choose from beeps 1-20 or 0 for random to playback
def play_panel_beep(beep):
    if 1 <= beep <= 20:
        fileno = beep
    elif beep == 0:
        fileno = randint(1,20)
    else:
        print("Invalid sound selection. Playing error sound")
        fileno = 27
    soundfile = (sounddir+"/panel_beeps/2{:02d}.wav".format(fileno))
    pyportal.play_file(soundfile)

# Scheduler that only pulls a new METAR from the API based upon the refresh threshold
def time_for_new_metar(last_metar_time):
    # We haven't gotten it at all yet
    if last_metar_time == 0:
        return True
    # we're on the minute-based threshold AND it's longer than the threshold away
    elif ((time.localtime().tm_min % metar_refresh) == 0) and ((time.time() - last_metar_time) >= 60):
        return True
    else: # Not time to update the METAR yet
        return False

# Helper: Assemble URL with parameters since on-board CircuitPython can't do params...
def assemble_url(url, params):
    separator = '&'
    parameters_strings = []
    for param in params.keys():
        parameters_strings.append(param+"="+str(params[param]))
    full_metar_url = url + separator.join(parameters_strings)
    print("URL: "+full_metar_url)
    return full_metar_url

## Loading from file only
def get_current_metar():
    # TEMP - open XML file
    metar_file = 'testmetar.xml'
    print("Opening local METAR file for testing")
    f = open(metar_file,'r')
    metars = extract_metar_from_xml(f)
    f.close()
    return metars

# change background image to match local flying conditions
def update_background(weather):
    pass

# Use data dictionary of text fields to update the content of the display
def update_screen_text(data):
    pass

# Helper: return local time string
def pretty_datetime(timestamp):
    timestring = "{0}/{1}".format(
        time.localtime(timestamp).tm_mon,
        time.localtime(timestamp).tm_mday
    )
    return timestring

# Helper: make clock string
def pretty_clock(timestamp):
    timestring = "{:02d}:{:02d}:{:02d}".format(
        time.localtime(timestamp).tm_hour,
        time.localtime(timestamp).tm_min,
        time.localtime(timestamp).tm_sec
        )
    return timestring

# Set screen brightness
def screen_brightness():
    pyportal.set_backlight(.8)

## Run scheduled activities
#def run_scheduler(last_metar_time):
#    
#    # Every minute, update the clock on-screen
#    if time.localtime().tm_sec % 59:
#        pyportal.set_text(pretty_lock(time.time()), index=1)
#        
#    # Every 15 minutes, update the METAR
#    if last_metar_time == 0:
#        response = pyportal.fetch()
#        play_panel_beep(2)
#
#    # we're on the minute-based threshold AND it's longer than the threshold away
#    elif ((time.localtime().tm_min % metar_refresh) == 0) and ((time.time() - last_metar_time) >= 60):
#        response = pyportal.fetch()
#        play_panel_beep(2)
        

#### END FUNCTION DEFINITIONS ####

#### INIT PORTAL ####
pyportal = PyPortal(
                        url=checkwx_metar_url,
                        headers=checkwx_header,
                        json_path=(raw_metar_text,station_id,flight_category),
                        status_neopixel=board.NEOPIXEL,
                        default_bg=metar_bg,
                        text_font=metar_font,
                        image_resize=(320,240),
                        image_position=(0,0),
                        text_position=((100,100),(250,12),(90,228)),
                        text_wrap=(30,0,0),
                        text_maxlen=(180,30,30),
                        text_color=(0xFFCC99,0x9999FF,0x000000)
                   )
#### END INIT PORTAL ####
# Play boot-up sound
play_panel_beep(20)

# Update device local time and preload the font
pyportal.preload_font()
pyportal.get_local_time()
screen_brightness()

#### Primary screen operation loop ####
while True:
    # Primary functions inside exception handler with 1-minute timeout.
    try:
        # Run any scheduled activities
        #run_scheduler(last_metar_time)
        
        # When screen is touched:
        if pyportal.touchscreen.touch_point:
            play_panel_beep(0)
        # If a new METAR is scheduled to be obtained
        if time_for_new_metar(last_metar_time):
            response = pyportal.fetch()
            play_panel_beep(2)
            last_metar_time = time.time()
    except Exception as e:
        print("Some error occured, retrying in 1 minute: ", e)
        pyportal.set_background(error_bg)
        pyportal.set_text('LCARS',index=2)
        play_offline_audio()
        time.sleep(60)
