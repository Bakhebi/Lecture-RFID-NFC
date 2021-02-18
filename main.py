DEBUG = False  # change to True to see debug messages

from pyscan import Pyscan
from MFRC630 import MFRC630
from LIS2HH12 import LIS2HH12
from LTR329ALS01 import LTR329ALS01
import binascii
import time
import pycom
import _thread
from mqtt import MQTTClient
import crypto
from crypto import AES
from network import WLAN
import machine

py = Pyscan()
nfc = MFRC630(py)
lt = LTR329ALS01(py)
li = LIS2HH12(py)

RGB_BRIGHTNESS = 0x8

RGB_RED = (RGB_BRIGHTNESS << 16)
RGB_GREEN = (RGB_BRIGHTNESS << 8)
RGB_BLUE = (RGB_BRIGHTNESS)

# Make sure heartbeat is disabled before setting RGB LED
pycom.heartbeat(False)

# Initialise the MFRC630 with some settings
nfc.mfrc630_cmd_init()

# MQTT paramètres
mqttClient = MQTTClient("ProjetCarte", "broker.hivemq.com", port=1883)
print(mqttClient.connect())

def Subscribe_handler(topic, msg):
    if(msg == b'0'):
        pycom.rgbled(RGB_GREEN)
        time.sleep(1)
    if(msg == b'1'):
        pycom.rgbled(RGB_RED)
        time.sleep(1)

mqttClient.set_callback(Subscribe_handler)

def print_debug(msg):
    if DEBUG:
        print(msg)

def send_sensor_data(name, timeout):
    while(True):
        print_debug(lt.light())
        print_debug(li.acceleration())
        time.sleep(timeout)

def discovery_loop(nfc, id):
    while True:
        mqttClient.subscribe(topic="listeappel2")
        # Send REQA for ISO14443A card type
        print_debug('Sending REQA for ISO14443A card type...')
        atqa = nfc.mfrc630_iso14443a_WUPA_REQA(nfc.MFRC630_ISO14443_CMD_REQA)
        print_debug('Response: {}'.format(atqa))
        if (atqa != 0):
            # A card has been detected, read UID*
            print_debug('A card has been detected, read UID...')
            uid = bytearray(10)
            uid_len = nfc.mfrc630_iso14443a_select(uid)
            print_debug('UID has length: {}'.format(uid_len))

            if (uid_len > 0):
                print_debug('Checking if card with UID: [{:s}] is listed in VALID_CARDS...'.format(binascii.hexlify(uid[:uid_len],' ').upper()))
                msgclaire = (binascii.hexlify(uid[:uid_len],' ').upper())
                mqttClient.publish(topic="listeappel", msg= msgclaire)
                pycom.rgbled(RGB_GREEN)
                print(msgclaire.decode('utf-8'))

        else:
            # No card detected
            #print_debug('Did not detect any card...')
            pycom.rgbled(RGB_BLUE)
        nfc.mfrc630_cmd_reset()
        time.sleep(.5)
        nfc.mfrc630_cmd_init()

# This is the start of our main execution... start the thread
_thread.start_new_thread(discovery_loop, (nfc, 0))
_thread.start_new_thread(send_sensor_data, ('Thread 2', 10))
