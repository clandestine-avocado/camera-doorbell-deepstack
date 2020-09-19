# Doorbell

### To Buy:
- Connectors for button, then resolder
- Flux | Flux Brush?
- Liquid elec tape
- Stand-off kit
- Heat sinks (5x)
- return screw driver kit
- Small pry bar kit to split Kindle Fire

### Project Goals:
Allow for doorbell press to:
- Capture still image and Record 20s video
- Sound a buzzer so doorbell user gets audible feedback of button press
- Send "doorbell/pressed" MQTT message to Home Assistant
- Node red automation listening for MQTT message
- Send push notifications (via Telegram?)

### Without button press, allow for object (person only) detection:
- Tensorflow ([Tensorflow HA Integration](https://www.home-assistant.io/integrations/tensorflow/) | [Install Page](https://www.tensorflow.org/install/)) 
- Tensorflow Lite
- DOODS ([DOODS HA Integration](https://www.home-assistant.io/integrations/doods/) | [DOODS in GIT](https://github.com/snowzach/doods))
- Other software?




# Equipment:
- [Rasperry Pi 3A](https://www.microcenter.com/product/514076/3_Model_A_Board?storeID=081)
- [Pi NoIR camera module](https://www.amazon.com/gp/product/B07W5T3J5T/ref=ppx_yo_dt_b_asin_title_o02_s00?ie=UTF8&psc=1)
- [Momentary button switch w/ LED backlight](https://www.aliexpress.com/item/32956631402.html?spm=a2g0s.9042311.0.0.73504c4dbyl6RU)
- [5V Piezo Buzzer (PASSIVE)](https://www.aliexpress.com/item/32974555488.html?spm=a2g0s.9042311.0.0.73504c4dbyl6RU) - Can play tune with PWM
- [5V Piezo Buzzer (ACTIVE)](https://www.amazon.com/gp/product/B07GL4MBLM/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&psc=1) - Plays simple tone only


# Wiring Diagram
![Imgur](https://imgur.com/JaFJqDj.png)



# Capture still image and Record 20s video


<insert python script>

### Getting Set up to Write Images and Video Directly to Home Assistant Directory
Install Samba client AND server on Pi. The server function will probably not be used from the Pi. In this set up, the Pi is acting as the client and the [Samba add-on in Home Assistant](https://www.home-assistant.io/getting-started/configuration/#editing-configuration-via-sambawindows-networking) is acting as the server, but better to have both anyway.
Install instructions I used are [here](https://www.raspberrypi.org/documentation/remote-access/samba.md)

### To mount a HA directory to Pi directory:
```sudo mount.cifs //HASSIO9/config/www/doorbell /home/pi/projects/doorbell  -o user=kevin```
- Server: //HASSIO9/config/www/doorbell is the host name + folder path
- Client: /home/pi/projects/doorbell is the client side + folder path
- Run the cmd and enter pwd when prompted. This works to mount mannually but **does not survive reboot!**
- To survive reboot, you must add a permenant mount; so far I have been unscessful

### Setting Up a Perm Mount [fstab] method
[This page](http://timlehr.com/auto-mount-samba-cifs-shares-via-fstab-on-linux/) has pretty clear instructions that got it working for me. I still need to figure out how to use credentials, however.

- Navigate to Pi's root: ```cd /```
- Edit fstab: ```sudo nano /etc/fstab```
- Enter below configuration, but DO NOT EDIT ANYTHING ELSE!

```
//HASSIO9/config/www/doorbell 	/home/pi/projects/doorbell 	cifs 	uid=0,username=*****,password=**********,iocharset=utf8,vers=3.0,noperm 0 0
```
- Reboot ```sudo reboot```

- Take test picture, store in mounted share folder: ```sudo raspistill -o "/home/pi/projects/doorbell/testpicture.jpg"```

- Verify the picture saved in the right place sucessfully:
```
pi@DB3A:~ $ cd /home/pi/projects/doorbell
pi@DB3A:~/projects/doorbell $ ls
testpicture.jpg  me.jpg  test1.jpg  testfordoorbellfolder.txt  testremounted1.jpg
pi@DB3A:~/projects/doorbell $ 
```

### Setting Up a Perm Mount [systemd] method

Using [this guide](https://anteru.net/blog/2019/automatic-mounts-using-systemd/) I did everything between the X's, it worked once, then fails to start. Probably a password/config issue in home-pi-projects-doorbell.mount file, but I can't figure it out. Therefore, to mount after boot, I'll just boot then run ```sudo mount -a``` manually for now.

xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
- In ```/etc/systemd/system``` create a file named ```home-pi-projects-doorbell.mount```
- ```cd /etc/systemd/system```
- ```sudo nano home-pi-projects-doorbell.mount```

```
==========================================
[Unit]
Description=myshare mount

[Mount]
What=//HASSIO9/config/www/doorbell
Where=/home/pi/projects/doorbell
Type=cifs
Options=rw,file_mode=0700,dir_mode=0700,uid=1000,user=********,password=********
DirectoryMode=0700
[Install]
WantedBy=multi-user.target
==========================================
```


- Also in ```/etc/systemd/system``` create a file named ```home-pi-projects-doorbell.automount```
- ```sudo nano home-pi-projects-doorbell.automount```
```
==========================================
[Unit]
Description=myshare automount

[Automount]
Where=/home/pi/projects/doorbell

[Install]
WantedBy=multi-user.target
==========================================
```

### This [home-pi-projects-doorbell.automount] is the unit we want to enable and start automatically, so we need to perform the following steps:

- ```systemctl daemon-reload```                            					to reload the configuration
- ```systemctl start home-pi-projects-doorbell.automount```   		to start the unit – so we can use it right away
- ```systemctl enable home-pi-projects-doorbell.automount``` 	 	to enable the auto-start of the unit
- ```systemctl status home-pi-projects-doorbell.automount```		  to check status






# MQTT 

**Goal**: After picture taken by the Pi cam on the Pi 3A (Doorbell), send a simple message to Home Assistant server running the [Mosquitto MQTT Broker Add-on](https://www.home-assistant.io/docs/mqtt/broker/). This will serve as a trigger for notifications in Home Assistant. This could be done with the [Folder Watcher integration](https://www.home-assistant.io/integrations/folder_watcher/)  within Home Assistant, but I was unable to get that working properly.

### Install Paho-MQTT and Testing Connection to HA:
- On the Pi 3A device, install [paho-mqtt](https://pypi.org/project/paho-mqtt/) via the ```pip install paho-mqtt``` command
- Create [testing_mqtt_con_to_HA.py](https://raw.githubusercontent.com/clandestine-avocado/doorbell/master/mqtt/testing_mqtt_con_to_HA.py?token=ANPVX4LI7RVCVN5HWXXXSOS7LYLVK) on the Pi 3A
- Subscribe to "DOORBELL" topic on the HA Mosquitto broker.
- Run testing_mqtt_con_to_HA.py and confirm DOORBELL topic is received



```python
#testing_mqtt_con_to_HA.py

import paho.mqtt.client as mqtt # Import the MQTT library

import time # The time library is useful for delays

 

# Our "on message" event

def messageFunction (client, userdata, message):

topic = str(message.topic)

message = str(message.payload.decode("utf-8"))

print(topic + message)

 

 

ourClient = mqtt.Client("pi3a_mqtt") # Create a MQTT client object

ourClient.connect("192.168.1.237", 1883) # Connect to the HA Mosquitto MQTT broker (or test MQTT broker @ test.mosquitto.org)

ourClient.subscribe("DOORBELL") # Subscribe to the topic DOORBELL

ourClient.on_message = messageFunction # Attach the messageFunction to subscription

ourClient.loop_start() # Start the MQTT client

 

 

# Main program loop

while(1):

ourClient.publish("DOORBELL", "on") # Publish message to MQTT broker

time.sleep(1) # Sleep for a second
```



# Add Passive Buzzer
![image placeholder](https://i0.wp.com/peppe8o.com/wp-content/uploads/2020/07/Raspberry-PI-passive-buzzer-wiring.jpg?w=826&ssl=1)

[This](https://peppe8o.com/use-passive-buzzer-with-raspberry-pi-and-python/) intro tutorial got me started to make sure my buzzer worked. It was then was modified later for my purposes.

```python
# Import required libraries
import sys
import RPi.GPIO as GPIO
import time

# Set trigger PIN according with your cabling
buzzerPIN = 14

# Set PIN to output
GPIO.setmode(GPIO.BCM)
GPIO.setup(buzzerPIN,GPIO.OUT)

# define PWM signal and start it on trigger PIN
buzzer = GPIO.PWM(buzzerPIN, 1000) # Set frequency to 1 Khz
buzzer.start(10) # Set dutycycle to 10

# this row makes buzzer work for 1 second, then
# cleanup will free PINS and exit will terminate code execution
time.sleep(1)

GPIO.cleanup()
sys.exit() # quits Python - needs to be removed once integrated into the main doorbell script - which needs to run all the time.

# Please find below some addictional commands to change frequency and
# dutycycle without stopping buzzer, or to stop buzzer:
#
# buzzer.ChangeDutyCycle(10)
# buzzer.ChangeFrequency(1000)
# buzzer.stop()

```


# Final Python Script for Taking a Picture, Sharing the picture, and pushing MQTT to HA, Combined:
```python

import RPi.GPIO as GPIO
import time
import picamera
import datetime as dt
import sys
import paho.mqtt.client as mqtt # import the MQTT library


#def MQTT messagefunction here
def messageFunction (client, userdata, message):
    topic = str(message.topic)
    message = str(message.payload.decode("utf-8"))
    print("MQTT Topic: " + topic + "/" + message)

MQTTClient=mqtt.Client("pi3a_mqtt") # Create a MQTT client object
MQTTClient.username_pw_set(username="kevinmqtt", password="kevinmqtt") #Set a username and optionally a password for broker authentication. Must be called be$
MQTTClient.connect("192.168.1.237", 1883) # Connect to the HA Mosquitto MQTT broker (or test MQTT broker @ test.mosquitto.org)
MQTTClient.subscribe("DOORBELL") # Subscribe to the topic DOORBELL
MQTTClient.on_message = messageFunction # Attach the messageFunction to subscription
MQTTClient.loop_start() # Start the MQTT client

GPIO.setmode(GPIO.BCM)
buzzerPIN = 14
buttonPIN = 18
GPIO.setup(14, GPIO.OUT)
GPIO.setup(buttonPIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


# define PWM signal and start it on trigger PIN
buzzer = GPIO.PWM(buzzerPIN, 3000) # Set frequency to 1 Khz




while True:
    input_state = GPIO.input(buttonPIN)
    if input_state == True:
        print('Button Pressed')
        MQTTClient.publish("DOORBELL", "on") # Publish message to MQTT broker
        buzzer.start(10) # Set dutycycle to 10
        time.sleep(0.2)
        with picamera.PiCamera() as camera:
            camera.resolution = (800, 600)
            camera.annotate_background = picamera.Color('black')
            camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            camera.start_preview()
            camera.capture('doorbell.jpg', use_video_port=True)
            # camera.start_recording('doorbell.h264')
            # camera.wait_recording(20)
        time.sleep(.5)
        buzzer.stop()

GPIO.cleanup()
# sys.exit()


```

# Installing "Motion" as Standalone (not MotionEyeOS)
- Tutorial start point [here](https://learn.adafruit.com/cloud-cam-connected-raspberry-pi-security-camera/dropbox-sync#pi-camera-v4l2-kernel-module-1611979-38), followed exactly, except for the Dropbox uploading, since I want to do other things (Tensorflow?) with the images.
- Stupid config question asked [here](https://github.com/Motion-Project/motion/issues/1205)
- Config Help [here](https://motion-project.github.io/4.1.1/motion_guide.html#output_pictures)


