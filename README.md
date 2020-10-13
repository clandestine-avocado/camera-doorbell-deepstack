# Doorbell

<details><summary>Dummy Expansion Code</summary>
<p>
Put stuff here
</p>
</details>


<details><summary>Systems & Common Commands</summary>
<p>


| Component                                                         	| System        	| Function                                                                                                                                                                                                                                                                                                      	| Commands                                                                                                                                                                                                                                                                                       	|
|-------------------------------------------------------------------	|---------------	|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	|
| [Motion App](https://motion-project.github.io/motion_config.html) 	| Pi3A          	| Detect motion events for Deepstack processing Take snapshots from Doorbell button presses                                                                                                                                                                                                                     	| Mount HASSIO directory: ```sudo mount -a``` Verify mount worked: ```sudo mount -l``` Manually start via ```sudo motion start -n``` Also can be set to run as daemon (to do) Set/Edit config: ```sudo nano etc/motion/motion.conf``` View Motion Log: ```sudo nano var/log/motion/motion.log``` 	|
| Py Script                                                         	| Pi3A          	| Run script to detect button presses of physical doorbell. Button press takes snapshot via Motion app.                                                                                                                                                                                                         	| Manually run via ```python projects/doorbell/db4.py```                                                                                                                                                                                                                                         	|
| [Deepstack](https://python.deepstack.cc/)                         	| Xubuntu VM    	| Server side processing for object/person detection Local Deepstack server queried via [Home Assistant Deepstack integration](https://github.com/robmarkcole/HASS-Deepstack-object) Motion events from Motion App save .jpg file; file then processed for persons If detected, notifications send via Telegram 	| Manually run via: ```sudo docker run --restart always -e VISION-DETECTION=True -v localstorage:/datastore -p 80:5000 \deepquestai/deepstack```                                                                                                                                                 	|
| Node Red                                                          	| HASSIO Add-On 	| Provides automation logic: MQTT Broker receives messages from Py script when doorbell pressed, send notification. Deepstack service call scans Motion event snapshot, routes to notification if person detected.                                                                                              	| None; Housed on ```Deepstack``` Tab                                                                                                                                                                                                                                                            	|

### Common Commands:
Mount HASSIO drive to DB3A:
```
sudo mount -a
```
List mounted drives:
```
sudo mount -l
```
```
cd projects/doorbell
```
Run main doorbell script manually:
```
python projects/doorbell/db4.py
```
Start Motion app:
```
sudo start motion -n
```
View/edit Motion config:
```
sudo nano /etc/motion/motion.conf
```
View Motion Log:
```
sudo nano /var/log/motion/motion.log
```


</p>
</details>










### Project Goals:
Allow for doorbell press to:
- Capture still image and Record 20s video
- Sound a buzzer so doorbell user gets audible feedback of button press
- Send "doorbell/pressed" MQTT message to Home Assistant
- Node red automation listening for MQTT message
- Send push notifications (via Telegram?)

### Without button press, allow for object (person only) detection:
- ~~Tensorflow ([Tensorflow HA Integration](https://www.home-assistant.io/integrations/tensorflow/) | [Install Page](https://www.tensorflow.org/install/))~~
- ~~Tensorflow Lite~~
- ~~DOODS ([DOODS HA Integration](https://www.home-assistant.io/integrations/doods/) | [DOODS in GIT](https://github.com/snowzach/doods))~~
- Local [Deepstack server](https://python.deepstack.cc/) paired with [@robmarkcole's Deepstack integration](https://github.com/robmarkcole/HASS-Deepstack-object)




# Equipment:
- [Rasperry Pi 3A](https://www.microcenter.com/product/514076/3_Model_A_Board?storeID=081)
- [Pi NoIR camera module](https://www.amazon.com/gp/product/B07W5T3J5T/ref=ppx_yo_dt_b_asin_title_o02_s00?ie=UTF8&psc=1)
- [Momentary button switch w/ LED backlight](https://www.aliexpress.com/item/32956631402.html?spm=a2g0s.9042311.0.0.73504c4dbyl6RU)
- [5V Piezo Buzzer (PASSIVE)](https://www.aliexpress.com/item/32974555488.html?spm=a2g0s.9042311.0.0.73504c4dbyl6RU) - Can play tune with PWM
- [5V Piezo Buzzer (ACTIVE)](https://www.amazon.com/gp/product/B07GL4MBLM/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&psc=1) - Plays simple tone only
- [Zulkit Project Box](https://www.amazon.com/gp/product/B07RTYYHK7/ref=ppx_yo_dt_b_asin_title_o02_s00?ie=UTF8&psc=1) - 3.94 x 2.68 x 1.97 inch
- Dell Optiplex 7010 USFF (16GB RAM) - Run's multiple VM's, including HASSIO and an instance of Xubuntu 


# Wiring Diagram
![Imgur](https://imgur.com/JaFJqDj.png)



# Capture still image and Record 20s video


<insert python script>

### Getting Set up to Write Images and Video Directly to Home Assistant Directory
Install Samba client AND server on Pi. The server function will probably not be used from the Pi. In this set up, the Pi is acting as the client and the [Samba add-on in Home Assistant](https://www.home-assistant.io/getting-started/configuration/#editing-configuration-via-sambawindows-networking) is acting as the server, but better to have both anyway.

![Imgur](https://i.imgur.com/brokkfL.png)




- Install instructions for setting up Samba on the Pi are [here](https://www.raspberrypi.org/documentation/remote-access/samba.md)
    - Update first via `sudo apt update`
    - Install Samba client and cifs utilities via `sudo apt install samba samba-common-bin smbclient cifs-utils`

Note: If all you want to do is be able to read/write to directories shared out by the Samba add on from the HA server, you can stop here and skip to mounting the HA directories to the Pi. However, if you also want to share [serve] out directories FROM the Pi, do the following: 

- Navigate to the configuration file for Samba via `cd /etc/samba/smb.conf`
- Edit the file by running `sudo nano /etc/samba/smb.conf'

At the bottom of the file, add the following lines:
```
[sambashare] # This is the name that will appear under \\your Pi IP\XXXX i.e. `\\192.168.1.223\sambashare`
    comment = My directory from the Pi  # Just a simple description
    path = /home/pi/sambashare          # Absolute file path to share out from Pi
    read only = no                      # Allows write permissions
    browsable = yes                     # Makes discoverable on network
```



<details><summary>### To mount a HA directory to Pi directory:</summary>
<p>
```sudo mount.cifs //HASSIO9/config/www/doorbell /home/pi/projects/doorbell  -o user=kevin```
- Server: //HASSIO9/config/www/doorbell is the host name + folder path
- Client: /home/pi/projects/doorbell is the client side + folder path
- Run the cmd and enter pwd when prompted. This works to mount mannually but **does not survive reboot!**
- To survive reboot, you must add a permenant mount; so far I have been unscessful
</p>
</details>



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


# Python Script for Taking a Picture, Sharing the picture, and pushing MQTT to HA, Combined:
- [x] Take a picture
- [x] Save the picture to mounted HA directory
- [x] Publish MQTT message to Mosquito Broker on HA

This script functions fine with the setup so far; however I would like to have motion detection and object recocnition running when the doorbell is *not* being pressed. Eventually, instead of using the ```camera.capture``` funtion to take snapshots, I will integrate Motion and call a snapshot via a HTTP request. 

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


MakerHTTP requests to Motion via [Webcontrol_parms](https://motion-project.github.io/motion_config.html#webcontrol_parms)

```
http://db3a:8080/0/config/list                                  #Lists all the configuration values for the camera.
http://db3a:8080/0/config/set?{parm}={value1}                   #Set the value for the requested parameter
http://db3a:8080/0/config/get?query={parm}                      #Return the value currently set for the parameter.
http://db3a:8080/0/config/write                                 #Write the current parameters to the file.
http://db3a:8080/0/detection/status                             #Return the current status of the camera.
http://db3a:8080/0/detection/connection                         #Return the connection status of the camera.
http://db3a:8080/0/detection/start                              #Start or resume motion detection.
http://db3a:8080/0/detection/pause                              #Pause the motion detection.
http://db3a:8080/0/action/eventstart                            #Trigger a new event.
http://db3a:8080/0/action/eventend                              #Trigger the end of a event.
http://db3a:8080/0/action/snapshot                              #Create a snapshot
http://db3a:8080/0/action/restart                               #Shutdown and restart Motion
http://db3a:8080/0/action/quit                                  #Close all connections to the camera
http://db3a:8080/0/action/end                                   #Entirely shutdown the Motion application
```

### Start Motion app:
```
sudo start motion -n
```

CURL in Python with [Requests](https://www.kite.com/python/answers/how-to-use-curl-in-python)
Other Python example to [activate Motion](https://github.com/ccrisan/motioneyeos/issues/842)



# TensorFlowLite
I used [this guide](https://github.com/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi/blob/master/Raspberry_Pi_Guide.md) to get started
