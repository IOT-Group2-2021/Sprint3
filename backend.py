#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Backend pour le projet IOT"""

__author__      = "Michaël da Silva, Guillaume Schranz, Nenad Rajic, Walid Massaoudi"
__copyright__   = "Copyright 2021, HEIG-VD"
__license__ 	= "GPL"
__version__ 	= "3.0"
__email__       = "michael.dasilva@heig-vd.ch, guillaume.schranz@heig-vd.ch, nenad.rajic@heig-vd.ch, walid.massaoudi@heig-vd.ch"
__status__ 		= "Prototype"

from os import error
import paho.mqtt.client as mqtt
import base64
import json
import datetime
import dateutil.parser as dparse
import dateutil.relativedelta as rdelta
import socket
import mysql.connector
"""
app_id = "iotheig"
access_key = "ttn-account-v2.dEG-dRa-JyxSqVG8VTsTLG6QDeM38BUwfNP-9Uq5ckY"
node1 = "intrusiondetector"
node2 = "cliknoise"
port_node1 = "1"
port_node2 = "2"
"""
# Test uniquement, TO DELETE
app_id = "iot-group2-2021"
access_key = "ttn-account-v2.h8BAs1uaCqT5y0vA1dEkqwz-yfvtCDUs-qx2na7aOiY"
node1 = "test-iot-group2-2021"
node2 = "test-iot-group2-2021-node2"
port_node1 = "1"

type_value = {3302: "Presence", 3303: "Temperature", 3304: "Humidity", 3315: "Pressure", 3324: "Loudness", 3325: "Concentration"}
symbol = {3302: "", 3303: "°C", 3304: "%", 3315: "hPa", 3324: "mV", 3325: "ppm"}

# Classe pour exception personnalisé
class Error(Exception):
    pass

class ErrorValue(Error):
    pass

class ErrorType(Error):
    pass

class ErrorNode(Error):
    pass

# Log les valeurs passées en arguments dans le fichier logs.log
def log_values(dt, topic, values):
    f = open("logs.log", "a+")
    f.write(dt + " - ")
    f.write("Valeur reçu de " + str(topic)+" : ")
    
    for value in values:
        f.write(type_value[value[0]] + " = " + str(value[1]) + " " + symbol[value[0]])
        if(values.index(value) != len(values) - 1):
            f.write(" / ")

    f.write("\n")
    f.close()

# Vérifie les valeurs reçues selon leur barême respectif
def check_values(type, value):    
    if(type == 3302):
        return True if 0 <= value <= 1 else False
    elif(type == 3303):
        return True if -40.0 <= value <= 85.0 else False  
    elif(type == 3304):
        return True if 0.0 <= value <= 100.0 else False  
    elif(type == 3315):
        return True if 300.0 <= value <= 1000.0 else False 
    elif(type == 3324):
        return True if 0.0 <= value <= 2000.0 else False
    elif(type == 3325):
        return True if 400 <= value <= 60000 else False
    else:
        print("error")
        raise ErrorValue

# Parser les données reçues par le payload
def parser_data(data):
    values = []

    while(data):
        type_number = int.from_bytes(data[:2], 'big')
        del data[:2]
        value = 0

        if(type_number == 3302):
            value = int.from_bytes(data[:1], 'big')
            del data[:1]
            values.append((3302, value))
            continue
        elif(type_number == 3303):
            value = int.from_bytes(data[:2], 'big', signed=True)/10
            del data[:2]
            values.append((3303, value))
            continue
        elif(type_number == 3304):
            value = int.from_bytes(data[:1], 'big')/2
            del data[:1]
            values.append((3304, value))
            continue
        elif(type_number == 3315):
            value = int.from_bytes(data[:2], 'big')/10
            del data[:2]
            values.append((3315, value))
            continue
        elif(type_number == 3324):
            value = int.from_bytes(data[:2], 'big')/10
            del data[:2]
            values.append((3324, value))
            continue
        elif(type_number == 3325):
            value = int.from_bytes(data[:2], 'big')
            del data[:2]
            values.append((3325, value))
            continue
        else:
            raise ErrorType

    return values

# Callback quand le client reçoit une réponse CONNACK depuis le serveur TTN.
def on_connect(client, userdata, flags, rc):
    dt = datetime.datetime.now().strftime("%Y-%m-%d %X")
    f = open("logs.log", "a+")
    f.write(dt+" - ")
    f.write("Connection with result code:"+str(rc)+"\n")
    f.close()
    # SUBSCRIBE sur tous les devices de l'application
    client.subscribe(app_id + '/devices/#')

# Log tous types de messages reçus via MQTT
def on_log(client, userdata, level, buf):
    # Logging avec temps et évenements géré par la librairie
    dt = datetime.datetime.now().strftime("%Y-%m-%d %X")
    f = open("logs.log", "a+")
    f.write(dt+" - "+buf)
    f.write("\n")
    f.close()

# Callback quand un message PUBLISH est reçu depuis le serveur.
def on_message(client, userdata, msg):
    data = None
    # Parsing du payload reçu
    j = json.loads(msg.payload)

    if "dev_id" in j:
        dev_id = j["dev_id"]
        payload_raw = j["payload_raw"]
        datetime = j["metadata"]["time"]

        # Parsing du datetime du payload + ajout d'une heure pour UTC+1 (Suisse)
        dt = dparse.parse(datetime)
        dt = dt + rdelta.relativedelta(hours=1)
        dt = dt.strftime("%Y-%m-%d %X")

        # Decodage de base64 en int du payload
        try:
            # Transformation du payload de base64 à bytes
            payload_decode = base64.b64decode(payload_raw)
            print("base64 to byte done")

            # Ecriture des informations du payload reçu dans un fichier log
            # (Datetime + Topic qui a envoyé le payload + payload entier)
            f = open("logs.log", "a+")
            f.write(dt+" - ")
            f.write(str(msg.topic)+"   ")
            f.write(str(msg.payload))
            f.write("\n")
            f.close()
            print("log du payload raw")

            # Capture de la portion de data à l'autre groupe pour l'envoi
            if(dev_id == node1):
                data = payload_decode[:3]
            elif(dev_id == node2):
                data = payload_decode[:4]
            else:
                raise ErrorNode
            print("capture data pour autre groupe done")

            # Parser les valeurs contenues dans le payload initial
            values = parser_data(bytearray(payload_decode))
            print("values parsé")

            # Vérifier chaque valeur selon leur barême
            for value in values:
                if(not check_values(value[0], value[1])):
                    raise ErrorValue
            print("values OK")

            # Log les valeurs reçus
            log_values(dt, dev_id, values)
            print("log des values done")

            # Ajout des valeurs dans la DB
            # TODO
            print("values ajouté à la DB")

            # Envoi des datas pour l'autre groupe
            print(data)
            print("data envoyé à l'autre groupe")
        
        except ErrorNode:
            f = open("logs.log", "a+")
            f.write(dt + " - ERROR : Le Node qui a envoyé le dernier paquet n'est pas valide\n")
            f.close()
        except ErrorType:
            f = open("logs.log", "a+")
            f.write(dt + " - ERROR : Le type d'une valeur reçue depuis le payload n'est pas valide\n")
            f.close()
        except ErrorValue:
            f = open("logs.log", "a+")
            f.write(dt + " - ERROR : Une des valeurs reçues du payload n'est pas valide\n")
            f.close()       
        except:
            f = open("logs.log", "a+")
            f.write(dt + " - ERROR : Erreur inconnue survenue durant le traitement du payload reçu\n")
            f.close()

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="IOTgroup2$",
    database="iot-group2"
)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_log = on_log

client.username_pw_set(app_id,access_key)
client.connect("eu.thethings.network", 1883, 60)
client.loop_forever()