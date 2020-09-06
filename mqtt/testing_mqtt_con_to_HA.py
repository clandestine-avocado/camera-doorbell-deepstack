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
