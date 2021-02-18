# Doorbell - A Work in Progress

<details><summary>Dummy Expansion Markup</summary>
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
- Local [Deepstack server](https://docs.deepstack.cc/) paired with @robmarkcole's [Deepstack integration](https://github.com/robmarkcole/HASS-Deepstack-object)




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


### Mounting Directories (Temp and Perm)
<details><summary>Temp Mount a HA directory to Pi directory:</summary>
<p>
    
```sudo mount.cifs //HASSIO9/config/www/doorbell /home/pi/projects/doorbell  -o user=kevin```

- Server: //HASSIO9/config/www/doorbell is the host name + folder path
- Client: /home/pi/projects/doorbell is the client side + folder path
- Run the cmd and enter pwd when prompted. This works to mount mannually but **does not survive reboot!**
- To survive reboot, you must add a permenant mount; so far I have been unscessful

</p>
</details>


<details><summary>Perm Mount: fstab method:</summary>
<p>
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
</p>
</details>


<details><summary>Perm Mount: systemd method:</summary>
<p>

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



</p>
</details>



# MQTT 

**Goal**: After picture taken by the Pi cam on the Pi 3A (Doorbell), send a simple message to Home Assistant server running the [Mosquitto MQTT Broker Add-on](https://www.home-assistant.io/docs/mqtt/broker/). This will serve as a trigger for notifications in Home Assistant. This could be done with the [Folder Watcher integration](https://www.home-assistant.io/integrations/folder_watcher/)  within Home Assistant, but I was [unable to get that working properly](https://community.home-assistant.io/t/folder-watcher-watchdog-component/45334/87?u=kr_noob).

### Install Paho-MQTT and Testing Connection to HA:
- On the Pi 3A device, install [paho-mqtt](https://pypi.org/project/paho-mqtt/) via the ```pip install paho-mqtt``` command
- Create [testing_mqtt_con_to_HA.py](https://raw.githubusercontent.com/clandestine-avocado/doorbell/master/mqtt/testing_mqtt_con_to_HA.py?token=ANPVX4LI7RVCVN5HWXXXSOS7LYLVK) on the Pi 3A
- Subscribe to "DOORBELL" topic on the HA Mosquitto broker.
- Run `testing_mqtt_con_to_HA.py` and confirm DOORBELL topic is received by HA Mosquitto broker


<details><summary>*Click to Expand MQTT test script...*</summary>
<p>

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

</p>
</details>



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
- [x] THIS KIND OF WORKED BUT I ENDED UP KILLING THIS AND USING MOTION (NEXT SECTION) TO TAKE THE PICTURES
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
MQTTClient.username_pw_set(username="YOUR-MQTT-USERNAME", password="YOUR-MQTT-PASSWORD") #Set a username and optionally a password for broker authentication. Must be called be$
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
- Tutorial start point [here](https://learn.adafruit.com/cloud-cam-connected-raspberry-pi-security-camera/dropbox-sync#pi-camera-v4l2-kernel-module-1611979-38), followed exactly, except for the Dropbox uploading, since I want to do other things locally like run them against a local Deepstack server for person detection to reduce false positive notifications.
- I asked some stupid config questions [here](https://github.com/Motion-Project/motion/issues/1205)
- Config Help [here](https://motion-project.github.io/4.1.1/motion_guide.html#output_pictures)


Make HTTP requests to Motion via [Webcontrol_parms](https://motion-project.github.io/motion_config.html#webcontrol_parms). This allows easy settings changes for the camera.

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
Once running, It will take pictures on motion detection and save them to a directory within Home Assistant. I set up a Node-Red flow to detect the new pictures, and send them off to a local Deepstack server for person detection. If a person is detected, the flow continues and sends a notification via Telegram.

I had issues keeping Motion running, and never was able to get that ironed out. I looked into a few ways, but didn't pan out for me.
- CURL in Python with [Requests](https://www.kite.com/python/answers/how-to-use-curl-in-python)
- Other Python example to [activate Motion](https://github.com/ccrisan/motioneyeos/issues/842)




### Final Node-Red Flow:

*Note: Like any self respecting Node Red flow, it's overly complicated and poorly designed. But it worked for me.* 

- Also included in the below flow is a sequence/flow that you can manually inject/trigger that will grab a random photo from [loremflickr](https://loremflickr.com) that should have a person in it - allowing you to test your deepstack function. 
- Add `/g/320/240/person/all` parameters to the end of the base URL [https://loremflickr.com] and paste in a browser - prety handy for testing.

```
[{"id":"fc77fc49.e8c85","type":"function","z":"fc65951e.1c69e8","name":"Prep Motion Photo msg","func":"\nmsg.method = \"sendPhoto\";\n\nmsg.payload = {\n    photo: \"/config/deepstack/deepstack_object_deepstack_frontdoor_person_latest.jpg\", \n    //\"/config/www/doorbell/motion/motion.jpg\"\n            \n    caption: \"Person Detected\"\n};\n\nreturn msg;\n\n","outputs":1,"noerr":0,"initialize":"","finalize":"","x":830,"y":2560,"wires":[["2f9e5365.0501dc"]]},{"id":"2f9e5365.0501dc","type":"telegrambot-payload","z":"fc65951e.1c69e8","name":"Send HA Alerts","bot":"7721b409.a414fc","chatId":"my-chat-id","sendMethod":"sendPhoto","payload":"","x":1080,"y":2560,"wires":[["b1bd855d.749198"]]},{"id":"b1bd855d.749198","type":"time-comp","z":"fc65951e.1c69e8","outputs":1,"name":"Time Stamp","positionConfig":"a3099cca.68263","input":"","inputType":"date","inputFormat":"0","inputOffset":0,"inputOffsetType":"none","inputOffsetMultiplier":60000,"rules":[],"checkall":"true","result1":"","result1Type":"msgPayload","result1Value":"","result1ValueType":"input","result1Format":"11","result1Offset":0,"result1OffsetType":"none","result1OffsetMultiplier":60000,"x":1310,"y":2560,"wires":[["e49d97cc.eae1c8"]]},{"id":"e49d97cc.eae1c8","type":"function","z":"fc65951e.1c69e8","name":"file name","func":"msg.payload = msg.payload + \"_motion.jpg\"\nreturn msg;","outputs":1,"noerr":0,"initialize":"","finalize":"","x":1460,"y":2560,"wires":[["e5faaabc.880218"]]},{"id":"7accefc8.d603f","type":"wfwatch","z":"fc65951e.1c69e8","d":true,"folder":"/config/www/doorbell/motion/","x":180,"y":2320,"wires":[["306f184a.46f3a8","3c0fc097.f948f"]]},{"id":"9e9528d3.64ba58","type":"api-call-service","z":"fc65951e.1c69e8","name":"Deepstack","server":"b1cff34f.02b12","version":1,"debugenabled":false,"service_domain":"image_processing","service":"scan","entityId":"image_processing.deepstack_object_deepstack_frontdoor_person","data":"","dataType":"json","mergecontext":"","output_location":"","output_location_type":"none","mustacheAltTags":false,"x":210,"y":2560,"wires":[["444364df.078e0c"]]},{"id":"444364df.078e0c","type":"api-current-state","z":"fc65951e.1c69e8","name":"Check State","server":"b1cff34f.02b12","version":1,"outputs":1,"halt_if":"","halt_if_type":"num","halt_if_compare":"is","override_topic":false,"entity_id":"image_processing.deepstack_object_deepstack_frontdoor_person","state_type":"str","state_location":"payload","override_payload":"msg","entity_location":"data","override_data":"msg","blockInputOverrides":false,"x":210,"y":2640,"wires":[["e907ab13.320b88"]]},{"id":"e907ab13.320b88","type":"switch","z":"fc65951e.1c69e8","name":"","property":"payload","propertyType":"msg","rules":[{"t":"gte","v":"1","vt":"num"},{"t":"eq","v":"unknown","vt":"str"},{"t":"eq","v":"0","vt":"num"}],"checkall":"true","repair":false,"outputs":3,"x":390,"y":2640,"wires":[["9a336529.3b8168"],["ddd99107.aa189"],["5a65995e.ff38b8"]]},{"id":"dccf2027.24ac1","type":"function","z":"fc65951e.1c69e8","name":"Deepstack Down","func":"\nmsg.method = \"sendMessage\";\n\nmsg.payload = {\n    text: \"DEEPSTACK is down\"\n};\n\nreturn msg;\n\n","outputs":1,"noerr":0,"initialize":"","finalize":"","x":850,"y":2640,"wires":[["d3519053.d9e67"]]},{"id":"d3519053.d9e67","type":"telegrambot-payload","z":"fc65951e.1c69e8","name":"Send HA Alerts","bot":"7721b409.a414fc","chatId":"my-chat-id","sendMethod":"sendMessage","payload":"","x":1080,"y":2640,"wires":[["6d6a0c9c.6fe6b4"]]},{"id":"fc1561e5.4b149","type":"http request","z":"fc65951e.1c69e8","name":"Get random test picture","method":"GET","ret":"bin","paytoqs":"ignore","url":"https://loremflickr.com/g/320/240/person/all","tls":"","persist":false,"proxy":"","authType":"","x":590,"y":2040,"wires":[["685eeabd.d2be24"]]},{"id":"b1164f1b.ffdda","type":"inject","z":"fc65951e.1c69e8","name":"Generate test image","props":[{"p":"payload"},{"p":"topic","vt":"str"}],"repeat":"","crontab":"","once":false,"onceDelay":0.1,"topic":"","payload":"","payloadType":"date","x":230,"y":2040,"wires":[["fc1561e5.4b149"]]},{"id":"3688dde9.f18e52","type":"image","z":"fc65951e.1c69e8","name":"","width":"300","data":"payload","dataType":"msg","thumbnail":true,"active":true,"pass":false,"outputs":0,"x":1060,"y":2040,"wires":[]},{"id":"685eeabd.d2be24","type":"jimp-image","z":"fc65951e.1c69e8","name":"","data":"payload","dataType":"msg","ret":"img","parameter1":"/config/www/doorbell/motion/motion.jpg","parameter1Type":"str","parameter2":"","parameter2Type":"msg","parameter3":"","parameter3Type":"msg","parameter4":"","parameter4Type":"msg","parameter5":"","parameter5Type":"msg","parameter6":"","parameter6Type":"msg","parameter7":"","parameter7Type":"msg","parameter8":"","parameter8Type":"msg","parameterCount":1,"jimpFunction":"write","selectedJimpFunction":{"name":"write","fn":"write","description":"Write to file. NOTE: You can specify an alternative file extension type to change the type. Currently support types are jpg, png, bmp.","parameters":[{"name":"filename","type":"str","required":true,"hint":"Name of the file","defaultType":"str"}]},"x":830,"y":2040,"wires":[["3688dde9.f18e52"]]},{"id":"9a336529.3b8168","type":"throttle","z":"fc65951e.1c69e8","name":"30s","throttleType":"time","timeLimit":"30","timeLimitType":"seconds","countLimit":0,"blockSize":0,"locked":false,"x":570,"y":2560,"wires":[["576fe2a3.2c7f0c","fc77fc49.e8c85"]]},{"id":"e5faaabc.880218","type":"fs-ops-copy","z":"fc65951e.1c69e8","name":"copy and store image","sourcePath":"/config/www/doorbell/motion/","sourcePathType":"str","sourceFilename":"motion.jpg","sourceFilenameType":"str","destPath":"/config/www/doorbell/motion/detected","destPathType":"str","destFilename":"payload","destFilenameType":"msg","link":false,"overwrite":false,"x":1660,"y":2560,"wires":[["8d4a91f7.fbf78"]]},{"id":"9e6a8889.1d3928","type":"api-call-service","z":"fc65951e.1c69e8","name":"SET TO: Detected","server":"b1cff34f.02b12","version":1,"debugenabled":false,"service_domain":"input_select","service":"select_option","entityId":"input_select.deepstack_status","data":"{\"option\":\"Detected\"}","dataType":"json","mergecontext":"","output_location":"","output_location_type":"none","mustacheAltTags":false,"x":2130,"y":2560,"wires":[[]]},{"id":"8d4a91f7.fbf78","type":"api-current-state","z":"fc65951e.1c69e8","name":"If not DETECTED","server":"b1cff34f.02b12","version":1,"outputs":2,"halt_if":"Detected","halt_if_type":"str","halt_if_compare":"is_not","override_topic":false,"entity_id":"input_select.deepstack_status","state_type":"str","state_location":"payload","override_payload":"msg","entity_location":"data","override_data":"msg","blockInputOverrides":false,"x":1910,"y":2560,"wires":[["9e6a8889.1d3928"],[]]},{"id":"5a65995e.ff38b8","type":"api-current-state","z":"fc65951e.1c69e8","name":"If not CLEAR","server":"b1cff34f.02b12","version":1,"outputs":2,"halt_if":"Clear","halt_if_type":"str","halt_if_compare":"is_not","override_topic":false,"entity_id":"input_select.deepstack_status","state_type":"str","state_location":"payload","override_payload":"msg","entity_location":"data","override_data":"msg","blockInputOverrides":false,"x":590,"y":2720,"wires":[["33704b9e.5b3984"],[]]},{"id":"33704b9e.5b3984","type":"api-call-service","z":"fc65951e.1c69e8","name":"SET TO: Clear","server":"b1cff34f.02b12","version":1,"debugenabled":false,"service_domain":"input_select","service":"select_option","entityId":"input_select.deepstack_status","data":"{\"option\":\"Clear\"}","dataType":"json","mergecontext":"","output_location":"","output_location_type":"none","mustacheAltTags":false,"x":860,"y":2720,"wires":[[]]},{"id":"6d6a0c9c.6fe6b4","type":"api-call-service","z":"fc65951e.1c69e8","name":"SET TO: Offline","server":"b1cff34f.02b12","version":1,"debugenabled":false,"service_domain":"input_select","service":"select_option","entityId":"input_select.deepstack_status","data":"{\"option\":\"Offline\"}","dataType":"json","mergecontext":"","output_location":"","output_location_type":"none","mustacheAltTags":false,"x":1300,"y":2640,"wires":[[]]},{"id":"ddd99107.aa189","type":"api-current-state","z":"fc65951e.1c69e8","name":"If not OFFLINE","server":"b1cff34f.02b12","version":1,"outputs":2,"halt_if":"Offline","halt_if_type":"str","halt_if_compare":"is_not","override_topic":false,"entity_id":"input_select.deepstack_status","state_type":"str","state_location":"payload","override_payload":"msg","entity_location":"data","override_data":"msg","blockInputOverrides":false,"x":600,"y":2640,"wires":[["dccf2027.24ac1"],[]]},{"id":"306f184a.46f3a8","type":"debug","z":"fc65951e.1c69e8","name":"STATE CHECK","active":false,"tosidebar":true,"console":false,"tostatus":false,"complete":"payload","targetType":"msg","statusVal":"","statusType":"auto","x":160,"y":2260,"wires":[]},{"id":"3c0fc097.f948f","type":"switch","z":"fc65951e.1c69e8","name":"/motion.jpg or /doorbell.jpg","property":"payload.filePath","propertyType":"msg","rules":[{"t":"eq","v":"/config/www/doorbell/motion/doorbell.jpg","vt":"str"},{"t":"eq","v":"/config/www/doorbell/motion/motion.jpg","vt":"str"}],"checkall":"true","repair":false,"outputs":2,"x":500,"y":2320,"wires":[["2def0319.13029c"],["6d277b07.308184","8faedf07.ef605"]]},{"id":"6d277b07.308184","type":"throttle","z":"fc65951e.1c69e8","name":"10s","throttleType":"time","timeLimit":"30","timeLimitType":"seconds","countLimit":0,"blockSize":0,"locked":false,"x":190,"y":2500,"wires":[["9e9528d3.64ba58"]]},{"id":"2def0319.13029c","type":"api-call-service","z":"fc65951e.1c69e8","name":"DB Helper Turn ON","server":"b1cff34f.02b12","version":1,"debugenabled":false,"service_domain":"input_boolean","service":"turn_on","entityId":"input_boolean.doorbell_last_min","data":"","dataType":"json","mergecontext":"","output_location":"","output_location_type":"none","mustacheAltTags":false,"x":830,"y":2260,"wires":[["6ff94715.a8cc78"]]},{"id":"6ff94715.a8cc78","type":"delay","z":"fc65951e.1c69e8","name":"","pauseType":"delay","timeout":"10","timeoutUnits":"seconds","rate":"1","nbRateUnits":"1","rateUnits":"second","randomFirst":"1","randomLast":"5","randomUnits":"seconds","drop":false,"x":1060,"y":2260,"wires":[["16f050aa.b57b0f"]]},{"id":"16f050aa.b57b0f","type":"api-call-service","z":"fc65951e.1c69e8","name":"DB Helper Turn OFF","server":"b1cff34f.02b12","version":1,"debugenabled":false,"service_domain":"input_boolean","service":"turn_off","entityId":"input_boolean.doorbell_last_min","data":"","dataType":"json","mergecontext":"","output_location":"","output_location_type":"none","mustacheAltTags":false,"x":1280,"y":2260,"wires":[[]]},{"id":"576fe2a3.2c7f0c","type":"jimp-image","z":"fc65951e.1c69e8","name":"","data":"/config/www/doorbell/motion/motion.jpg","dataType":"str","ret":"img","parameter1":"","parameter1Type":"msg","parameter2":"","parameter2Type":"msg","parameter3":"","parameter3Type":"msg","parameter4":"","parameter4Type":"msg","parameter5":"","parameter5Type":"msg","parameter6":"","parameter6Type":"msg","parameter7":"","parameter7Type":"msg","parameter8":"","parameter8Type":"msg","parameterCount":0,"jimpFunction":"greyscale","selectedJimpFunction":{"name":"greyscale","fn":"greyscale","description":"remove colour from the image","parameters":[]},"x":680,"y":2440,"wires":[["16c92b53.735765"]]},{"id":"16c92b53.735765","type":"jimp-image","z":"fc65951e.1c69e8","name":"gscale_motion.jpg","data":"payload","dataType":"msg","ret":"img","parameter1":"/config/www/doorbell/motion/motion.jpg","parameter1Type":"str","parameter2":"","parameter2Type":"msg","parameter3":"","parameter3Type":"msg","parameter4":"","parameter4Type":"msg","parameter5":"","parameter5Type":"msg","parameter6":"","parameter6Type":"msg","parameter7":"","parameter7Type":"msg","parameter8":"","parameter8Type":"msg","parameterCount":1,"jimpFunction":"write","selectedJimpFunction":{"name":"write","fn":"write","description":"Write to file. NOTE: You can specify an alternative file extension type to change the type. Currently support types are jpg, png, bmp.","parameters":[{"name":"filename","type":"str","required":true,"hint":"Name of the file","defaultType":"str"}]},"x":890,"y":2440,"wires":[["2621a2cf.e8762e","17c04c05.f2bba4"]]},{"id":"2621a2cf.e8762e","type":"image","z":"fc65951e.1c69e8","name":"","width":"100","data":"payload","dataType":"msg","thumbnail":true,"active":true,"pass":false,"outputs":0,"x":1160,"y":2440,"wires":[]},{"id":"17c04c05.f2bba4","type":"function","z":"fc65951e.1c69e8","name":"Prep Motion Photo msg","func":"\nmsg.method = \"sendPhoto\";\n\nmsg.payload = {\n    photo: \"/config/www/doorbell/motion/motion.jpg\", \n    //\"/config/www/doorbell/motion/motion.jpg\"\n            \n    caption: \"Person Detected\"\n};\n\nreturn msg;\n\n","outputs":1,"noerr":0,"initialize":"","finalize":"","x":850,"y":2500,"wires":[["2f9e5365.0501dc"]]},{"id":"fd3b940.56fe97","type":"image","z":"fc65951e.1c69e8","name":"","width":"100","data":"payload","dataType":"msg","thumbnail":true,"active":true,"pass":false,"outputs":0,"x":1000,"y":2320,"wires":[]},{"id":"8faedf07.ef605","type":"jimp-image","z":"fc65951e.1c69e8","name":"","data":"/config/www/doorbell/motion/motion.jpg","dataType":"str","ret":"img","parameter1":"","parameter1Type":"msg","parameter2":"","parameter2Type":"msg","parameter3":"","parameter3Type":"msg","parameter4":"","parameter4Type":"msg","parameter5":"","parameter5Type":"msg","parameter6":"","parameter6Type":"msg","parameter7":"","parameter7Type":"msg","parameter8":"","parameter8Type":"msg","parameterCount":0,"jimpFunction":"none","selectedJimpFunction":{"name":"none","fn":"none","description":"Just loads the image.","parameters":[]},"x":810,"y":2320,"wires":[["fd3b940.56fe97"]]},{"id":"7721b409.a414fc","type":"telegrambot-config","botname":"BOT1","usernames":"","chatIds":"","pollInterval":"300"},{"id":"a3099cca.68263","type":"position-config","name":"timez","isValide":"true","longitude":"0","latitude":"0","angleType":"deg","timeZoneOffset":"99","timeZoneDST":"0","stateTimeFormat":"3","stateDateFormat":"12"},{"id":"b1cff34f.02b12","type":"server","name":"Home Assistant","legacy":false,"addon":true,"rejectUnauthorizedCerts":true,"ha_boolean":"y|yes|true|on|home|open","connectionDelay":true,"cacheJson":true}]
```





