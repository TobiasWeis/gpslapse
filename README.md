timelapse grabber and renderer for automotive sequences

Result of this code can be seen here:
http://www.team-afk.de/mega-timelapse-die-erste/

Usage: 

(1) Grabbing:
Connect a usb-camera and a GPS-device to your computer, then edit grabber/config.ini, adjust image size and folders ( note: create specified folder manually)
- run grabber/main.py

(2) Rendering:
- run balticmap.py
- run concat.py

(3) Make video:
- use a program like avconv to create a video from the still-frames ( conc_%08d.png)
