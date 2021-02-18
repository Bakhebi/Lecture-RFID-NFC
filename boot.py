import machine
from machine import UART
import os
from network import WLAN
import time


uart = UART(0, 115200)
os.dupterm(uart)

machine.main('main.py')

wlan = WLAN(mode=WLAN.STA)
wlan.connect(ssid='Mangue', auth=(WLAN.WPA2, 'jeanhive'))
print("WiFi connection in progress...")
if not wlan.isconnected():
    # machine.idle()
    time.sleep(2)
    wlan.connect(ssid='Mangue', auth=(WLAN.WPA2, 'jeanhive'))
print("WiFi connected succesfully")
print(wlan.ifconfig())

