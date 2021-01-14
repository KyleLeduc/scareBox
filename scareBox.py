#Libraries
import RPi.GPIO as GPIO
import time
import random
 
import os
from subprocess import Popen, PIPE
music = None

# Array averaging function
def Average(d):
    return round(sum(d) / len(d), 2)

print("Scare Box Running..")

# distanceBuffer init
distanceBuffer = [200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200]
minDistance = 300

# Amount of times sound file played
playCount = 0

# Timeout Tracking
timeoutCount = 0

# Sound file list to be picked from
soundLibrary = [
    '/home/pi/Documents/scareBox/BroodmotherSounds/feeding-time.mp3',
    '/home/pi/Documents/scareBox/BroodmotherSounds/feel-my-fangs.mp3',
    '/home/pi/Documents/scareBox/BroodmotherSounds/ill-drink-you-dry.mp3',
    '/home/pi/Documents/scareBox/BroodmotherSounds/was-that-a-twitch.mp3',
    '/home/pi/Documents/scareBox/BroodmotherSounds/we-shall-feast.mp3',
    '/home/pi/Documents/scareBox/BroodmotherSounds/who-dares-tug-my-web.mp3',
    '/home/pi/Documents/scareBox/BroodmotherSounds/youre-not-afraid-of-spiders-are-you.mp3'
]

#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
 
def playSound():
    global playCount, timeoutCount
    playCount += 1
    timeoutCount += 1
    os.system('mpg321 ' + random.choice(soundLibrary))
    time.sleep(10)
 
def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
 
if __name__ == '__main__':
    try:
        while True:
            dist = distance()
            if len(distanceBuffer) > 10:
                distanceBuffer.pop(0)
                distanceBuffer.append(dist)
            else:
                distanceBuffer.append(dist)
            average = Average(distanceBuffer)
            if average < minDistance:
                minDistance = average
            if average < 110:
                playSound()
                distanceBuffer.clear()
                distanceBuffer = [200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200]
            print("avg:" + str(average) + " actual:" + str(dist))
            time.sleep(0.3)
            if timeoutCount >= 3:
                timeoutCount = 0
                time.sleep(20)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        print ("Sound Played %.1f times" % playCount)
        print ("Minimum recorded distance was %.1f" % minDistance)
        GPIO.cleanup()