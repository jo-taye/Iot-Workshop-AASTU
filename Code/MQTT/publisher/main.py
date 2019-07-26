from network import WLAN
from mqtt import MQTTClient
import machine
import time
import pycom

import ucrypto
import math
import ujson

wifi_ssid = "IOT3"
wifi_passwd = "12345678"

broker_addr = "mqtt.thingspeak.com"
#MYDEVID = "PM"



CHANNEL_ID = "833686"
API_WRITE_KEY = "8MFQARUEMVU1X2VI"

MYDEVID = "channels/" + CHANNEL_ID + "/publish/" + API_WRITE_KEY

#String topicString ="channels/" + String( channelID ) + "/publish/"+String(writeAPIKey);


def settimeout(duration):
   pass

def random_in_range(l=0, h=1000):
    # r1 = ucrypto.getrandbits(32)
    # r2 = ((r1[0]<<24) + (r1[1]<<16) + (r1[2]<<8) + r1[3]) / 2**32
    return 1

def get_data_from_sensor(sensor_id="RAND"):
    if sensor_id == "RAND":
        return random_in_range()

def on_message(topic, msg):
    # just in case
    print("topic is: " + str(topic))
    print("msg is: " + str(msg))

pycom.heartbeat(False) # Disable the heartbeat LED

wlan = WLAN(mode=WLAN.STA)
nets = wlan.scan()
for net in nets:
    if net.ssid == wifi_ssid:
        print("Network " + wifi_ssid + " found!")
        wlan.connect(net.ssid, auth=(0, wifi_passwd), timeout=5000)
        # wlan.connect(net.ssid, auth=(net.sec, wifi_passwd), timeout=5000)
        while not wlan.isconnected():
            machine.idle() # save power while waiting
        print("WLAN connection succeeded!")
        print (wlan.ifconfig())
        break


client = MQTTClient("umqtt_client", broker_addr, user="yohannestaye", password=API_WRITE_KEY, port=1883)
client.connect()


while True:
    print("DATA: " + str(get_data_from_sensor()))
    client.publish(topic=MYDEVID, msg="field1=" + str(get_data_from_sensor()))
    time.sleep(1)
