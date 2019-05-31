#!/usr/bin/env python

import time, board, requests
from adafruit_pyportal import PyPortal
import xml.etree.ElementTree as ET

# Set up where we'll be fetching data from - prelim hard-code
DATA_SOURCE = "https://www.aviationweather.gov/adds/dataserver_current/"
DATA_PARAMS = "httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=KASH%20KCON%20KFIT"

# the current working directory (where this file is)
cwd = ("/"+__file__).rsplit('/', 1)[0]

def create_json_path(xmlinput):
    pass

def get_current_metar(url, params):
    try:
        r = requests.get(url+params)
        if r.headers['content-type'] == 'application/xml':
            xml_response = r.text
        else:
            print("URL returned wrong data type")
            return None
    except:
        print ("Can't obtain METAR from API: ",e)
        return None

pyportal = PyPortal(url=DATA_SOURCE,
                    json_path=(METAR_LOCATION, CODE_LOCATION),
                    status_neopixel=board.NEOPIXEL,
                    default_bg=cwd+"/images/capesuzette.bmp",
                    text_font=cwd+"/fonts/Arial-ItalicMT-17.bdf",
                    image_resize=(320,240),
                    image_position=(0,0),
                    text_position=((20, 120),  # METAR location
                                   (5, 210)), # airport code location
                    text_color=(0xFFFFFF,  # METAR text color
                                0x8080FF), # airport code text color
                    text_wrap=(35, # characters to wrap for METAR
                               0), # no wrap for airport code
                    text_maxlen=(180, 30), # max text size for both
                   )

# speed up projects with lots of text by preloading the font!
pyportal.preload_font()

while True:
    try:
        value = pyportal.fetch()
        print("Response is", value)
    except RuntimeError as e:
        print("Some error occured, retrying! -", e)
    time.sleep(60*5) # Update every 5 minutes
