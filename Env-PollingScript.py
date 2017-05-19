#!/usr/bin/python

import paho.mqtt.client as paho
import os
import socket
import ssl
import json
import time
from sense_hat import SenseHat

connflag = False

def on_connect(client, userdata, flags, rc):
    global connflag
    connflag = True
    if rc==0:
        print ("Connection status: successful")
    elif rc==1:
        print ("Connection status: Connection refused")

sense = SenseHat()

mqttc = paho.Client()
mqttc.on_connect = on_connect

awshost = "a16qzy7tmyv2qb.iot.eu-west-1.amazonaws.com"
awsport = 8883
clientId = "pi-garage"
thingName = "pi-garage"
caPath = "root-CA.crt"
certPath = "pi-garage.cert.pem"
keyPath = "pi-garage.private.key"

mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
mqttc.connect(awshost, awsport, keepalive=60)

mqttc.loop_start()

while True:

    message = {}

    device = {}
    device['cpuTemperature'] = os.popen('vcgencmd measure_temp').readline().replace("temp=","").replace("'C\n","")

    hostname = socket.gethostname()

    timestamp = int(time.time())

    environment = {}

    temp = {}
    temp['basedOnHumidity'] = sense.get_temperature_from_humidity()
    temp['basedOnPressure'] = sense.get_temperature_from_pressure()

    environment['humidity'] = sense.get_humidity()
    environment['pressure'] = sense.get_pressure()
    environment['temperature'] = temp
    environment['hostname'] = hostname
    environment['timestamp'] = timestamp

    message['device'] = device
    message['environment'] = environment

    jsonData = json.dumps(message)

    if connflag == True:
        mqttc.publish("environmentData", jsonData, qos=1)
        print jsonData
        time.sleep(10)
    else:
        print("waiting for connection...")
        time.sleep(5)

