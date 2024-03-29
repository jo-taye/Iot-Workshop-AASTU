import machine
from network import WLAN
wlan = WLAN(mode=WLAN.STA)

nets = wlan.scan()
for net in nets:
    if net.ssid == 'lopy-wlan-2df4':
        print('Network found!')

        wlan.connect(net.ssid, auth=(net.sec, 'www.pycom.io'), timeout=5000)
        while not wlan.isconnected():
            machine.idle() # save power while waiting
        print('WLAN connection succeeded!')
        break
