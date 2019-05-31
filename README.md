# pyportal-metar
Display airport METAR on Adafruit PyPortal IoT display device
Themed after Star Trek: TNG LCARS displays
Currently pulls the most recent METAR text for a hard-coded ICAO code airfield

### You will need:
An Adafruit pyPortal or other compatible device with 320x240 display,
and your secrets.py file configured with:
* Your wifi settings
* aio username and key
* API key for CheckWX (get one for free at https://www.checkwx.com)

## code.py
Main code which auto-executes.  Set your local airfield ICAO in here.

## /images
Zip file of .bmp images used by the app.  Unzip content into /images

## Future features underway:

* Support TAF, SIGMET and NOTAMs for the airfield and nearby area
* Select between the above options using the touchscreen
* "Configuration" screen which allows changing ICAO and other settings
