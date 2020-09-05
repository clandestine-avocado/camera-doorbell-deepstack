
import RPi.GPIO as GPIO
import time
import picamera
import datetime as dt

from gpiozero import Buzzer
from time import sleep



GPIO.setmode(GPIO.BCM)
buzzer = Buzzer(17)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

while True:
    input_state = GPIO.input(18)
    if input_state == True:
        print('Button Pressed')
        time.sleep(0.2)
        with picamera.PiCamera() as camera:
            camera.resolution = (800, 600)
            camera.annotate_background = picamera.Color('black')
            camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            camera.start_preview()
            camera.capture('doorbell.jpg', use_video_port=True)

        #make buzzer sounds here
        buzzer.on()
        sleep(2)
        print('buzzer sounds...')
        buzzer.off()
        sleep(2)        
        print('buzzer sounds...')
            
            
        with picamera.PiCamera() as camera:
            camera.resolution = (800, 600)
            camera.annotate_background = picamera.Color('black')
            camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            camera.start_preview()
            camera.start_recording('doorbell.h264')
            camera.wait_recording(20)
