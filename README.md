# doorbell

Project Goals:
Allow for doorbell press to:
- Capture still image and Record 20s video
- Sound a buzzer so doorbell user gets audible feedback of button press
- Send "doorbell/pressed" MQTT message to Home Assistant
- Node red automation listening for MQTT message
- Send push notifications (via Telegram?)

Without button press, allow for object (person only) detection:
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
![image placeholder](https://www.jameco.com/Jameco/workshop/circuitnotes/raspberry_pi_circuit_note_fig2a.jpg)



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

**Goal**: After picture taken by the Pi cam on the Pi 3A (Doorbell), send a simple message to Home Assistant server running the [Mosquitto MQTT Broker Add-on](https://www.home-assistant.io/docs/mqtt/broker/).

### Install and Testing Connection:
- On the Pi 3A device, install [paho-mqtt](https://pypi.org/project/paho-mqtt/) via the ```pip install paho-mqtt``` command
- Create [testing_mqtt_con_to_HA.py](https://raw.githubusercontent.com/clandestine-avocado/doorbell/master/mqtt/testing_mqtt_con_to_HA.py?token=ANPVX4PEY5A46BDX22IIAIC7KTDMS) on the Pi 3A
- Subscribe to "DOORBELL" topic on the HA Mosquitto broker.
- Run testing_mqtt_con_to_HA.py and confirm DOORBELL topic is received


```
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

I followed [this](https://peppe8o.com/use-passive-buzzer-with-raspberry-pi-and-python/) intro tutorial, then modified for my purposes.






