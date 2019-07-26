import machine
from network import WLAN
import pycom
wlan = WLAN(mode=WLAN.STA)

nets = wlan.scan()
print(nets)

while True:
    for net in nets:
        if net.ssid == "Ethiopia":
            rssid = net.rssi
            if rssid < -80:
                pycom.rgbled(0x7f0000)

            elif rssid >= -80 and rssid <= -70:
                pycom.rgbled(0x7f7f00)

            elif rssid > -70:
                pycom.rgbled(0x007f00)


        print(net.ssid, net.rssi)
