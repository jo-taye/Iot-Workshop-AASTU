from network import WLAN
from mqtt import MQTTClient
from pysense import Pysense
from SI7006A20 import SI7006A20
import pycom
import micropython
import machine
import time

import ucrypto
import math
import ujson

from pysense import Pysense
from LTR329ALS01 import LTR329ALS01

wifi_ssid = "IOT3"
wifi_passwd = "12345678"

broker_addr = "mqtt.thingspeak.com"
#MYDEVID = "PM"



CHANNEL_ID = "833674"
API_WRITE_KEY = "8M99L40HT47TP7Y6"

MYDEVID = "channels/" + CHANNEL_ID + "/publish/" + API_WRITE_KEY

#String topicString ="channels/" + String( channelID ) + "/publish/"+String(writeAPIKey);


def settimeout(duration):
   pass

def random_in_range(l=0, h=1000):
    r1 = ucrypto.getrandbits(32)
    r2 = ((r1[0]<<24) + (r1[1]<<16) + (r1[2]<<8) + r1[3]) / 2**32
    return math.floor(r2*h + l)

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
        wlan.connect(net.ssid, auth=(net.sec, wifi_passwd), timeout=5000)
        while not wlan.isconnected():
            machine.idle() # save power while waiting
        print("WLAN connection succeeded!")
        print (wlan.ifconfig())
        break

# client = MQTTClient(MYDEVID, broker_addr, 1883)
#
#
# if not client.connect():
#     print ("Connected to broker: " + broker_addr)
#
# print("Sending messages ...")
#
# while True:
#     # creating the data
#     the_data = get_data_from_sensor()
#
#     # publishing the data
#     the_data_json = ujson.dumps(the_data)
#     # client.publish(MYDEVID + "/value", the_data_json)
#     print(the_data_json)
#     # client.publish(MYDEVID + "/field_1", the_data_json)
#     client.publish(MYDEVID, field_1=the_data_json)
#     time.sleep(1)
def raw2Lux(CHRegs):
    # initial setup.
    # The initialization parameters in LTR329ALS01.py are:
    # gain: ALS_GAIN_1X, integration time: ALS_INT_100
    #
    gain = 0                        # gain: 0 (1X) or 7 (96X)
    integrationTimeMsec = 100       # integration time in ms

    # Determine if either sensor saturated (0xFFFF)
    # If so, abandon ship (calculation will not be accurate)
    if ((CHRegs[0] == 0xFFFF) or (CHRegs[1] == 0xFFFF)):
        lux = -1
        return(lux)
    # to calc correctly ratio, the CHRegs[0] must be != 0
    if (CHRegs[0] == 0x0000):
        lux = -1
        return(lux)

    # Convert from unsigned integer to floating point
    d0 = float(CHRegs[0])
    d1 = float(CHRegs[1])

    # We will need the ratio for subsequent calculations
    ratio = d1 / d0;

    # Normalize for integration time
    d0 = d0 * (402.0/integrationTimeMsec)
    d1 = d1 * (402.0/integrationTimeMsec)

    # Normalize for gain
    if (gain == 0):
        d0 = d0 * 16
        d1 = d1 * 16

    # Determine lux per datasheet equations:
    if (ratio < 0.5):
        lux = 0.0304 * d0 - 0.062 * d0 * math.pow(ratio,1.4)
        return(lux)

    if (ratio < 0.61):
        lux = 0.0224 * d0 - 0.031 * d1
        return(lux)

    if (ratio < 0.80):
        lux = 0.0128 * d0 - 0.0153 * d1
        return(lux)

    if (ratio < 1.30):
        lux = 0.00146 * d0 - 0.00112 * d1
        return(lux)

    lux = 0.0           # if (ratio > 1.30)
    return(lux)

# -----------------------------------------------------------

client = MQTTClient("umqtt_client", broker_addr, user="solwub16", password=API_WRITE_KEY, port=1883)
client.connect()
py = Pysense()
tempHum = SI7006A20(py)
ambientLight = LTR329ALS01(py)
while True:
    temperature = tempHum.temp()
    humidity = tempHum.humidity()
    print("Temperature: {} Degrees  Humidity: {}".format(temperature, humidity))
#    time.sleep(1)
            # class
    data = []
    # get 16 bit CH0 & CH1 registers
    data = ambientLight.lux()
    # print CH0 & CH1 registers
    LuxValue = raw2Lux(data)
    print("Read Ambient Light registers: {}   Lux: {}".format(data, LuxValue))
    #time.sleep(1)

    print("DATA: " + str(temperature))
    client.publish(topic=MYDEVID, msg="field1=" + str(temperature))
    client.publish(topic=MYDEVID, msg="field2=" + str(humidity))
    client.publish(topic=MYDEVID, msg="field3=" + str(LuxValue))
time.sleep(1)
