import qi
import time
import random
import sys

# IP = raw_input() 
IP = "192.168.1.103" 

session = qi.Session()
session.connect(IP)

try:
    tabletService = session.service("ALTabletService")

    # Display a local image located in img folder in the root of the web server
    # The ip of the robot from the tablet is 198.18.0.1
    tabletService.showImage("http://198.18.0.1/apps/img/4.png")
    time.sleep(10)
    # Hide the web view
    tabletService.hideImage()
except Exception as e:
    print(e)
    print("Error during the show image operation")