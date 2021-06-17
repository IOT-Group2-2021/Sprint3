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
from bot_envoi import *
import paho.mqtt.client as mqtt
import base64
import json
import datetime
import dateutil.parser as dparse
import dateutil.relativedelta as rdelta
import socket
import threading
import mysql.connector

app_id = "iotheig"
access_key = "ttn-account-v2.dEG-dRa-JyxSqVG8VTsTLG6QDeM38BUwfNP-9Uq5ckY"
node1 = "intrusiondetector"
node2 = "cliknoise"
port_node1 = "1"
port_node2 = "2"

type_value = {3302: "Presence", 3303: "Temperature", 3304: "Humidity", 3315: "Pressure", 3324: "Loudness", 3325: "Concentration"}
symbol = {3302: "", 3303: "°C", 3304: "%", 3315: "hPa", 3324: "mV", 3325: "ppm"}

HOST_SRC = '0.0.0.0'  # The server's hostname or IP address
PORT_SRC = 5678        # The port used by the server
HOST_DST = '10.192.75.85'  # The server's hostname or IP address
PORT_DST = 4567        # The port used by the server

# Classe pour exception personnalisé
class Error(Exception):
    pass

class ErrorValue(Error):
    pass

class ErrorType(Error):
    pass

# Ecriture dans la DB MySQL des différents types de données
def insert_db(datetime, values):
    mycursor = mydb.cursor()
    sql = ""
    val = ()
    type_data = values[0]
    data = values[1]

    if(type_data == 3302):
        sql = "INSERT INTO presence (datetime, data) VALUES (%s,%s)"
    elif(type_data == 3303):
        sql = "INSERT INTO temperature (datetime, data) VALUES (%s,%s)"
    elif(type_data == 3304):
        sql = "INSERT INTO rh (datetime, data) VALUES (%s,%s)"
    elif(type_data == 3315):
        sql = "INSERT INTO pressure (datetime, data) VALUES (%s,%s)"
    elif(type_data == 3324):
        sql = "INSERT INTO loudness (datetime, data) VALUES (%s,%s)"
    elif(type_data == 3325):
        sql = "INSERT INTO concentration (datetime, data) VALUES (%s,%s)"

    val = (datetime, data)

    mycursor.execute(sql, val)
    mydb.commit()

# Envoie des données vers l'autre groupe
def send_data(dt, data):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    try:
        s.connect((HOST_DST, PORT_DST))
        s.sendall(data)

        f = open("logs.log", "a+")
        f.write(dt + " - Envoi de data vers le backend2\n")
        f.close()
    except:
        f = open("logs.log", "a+")
        f.write(dt + " - Error: Le serveur backend2 est indisponible (timeout 5 sec)\n")
        f.close()

# Serveur socket TCP pour la réception des données de l'autre groupe
def socket_server():
    f = None
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST_SRC, PORT_SRC))
    s.listen()
    
    try:
        while True:
            dt = datetime.datetime.now().strftime("%Y-%m-%d %X")
            data = bytearray()

            f = open("server_socket.log", "a+")
            f.write("Waiting for a connection...\n")
            f.flush()

            (conn, addr) = s.accept()
            f.write('Connected from: ' + addr[0] + "\n")
            f.flush()
            f.close()
            # Réception des données de l'autre groupe
            while True:
                d = conn.recv(32)
                data += d
                if not d:
                    break

            f = open("logs.log", "a+")
            f.write(dt+" - Reçu de backend2\n")
            f.close()

            f = open("server_socket.log", "a+")
            f.write('Disconnected from: ' + addr[0] + "\n")
            f.close()
            
            try:
                # Parse les données
                values = parser_data(bytearray(data))
                # Check les données et si le type est celui dont a besoin l'autre groupe, ces données sont directement envoyées
                for value in values:
                    if(not check_values(value[0], value[1])):
                        raise ErrorValue
                    if(value[0] == 3304):
                        msg = (3304).to_bytes(2, "big") + (int(value[1] *2)).to_bytes(1, "big")
                        msg = base64.b64encode(msg)
                        msg = msg.decode('ascii')
                        publish_node(msg, node1, port_node1)
                    elif(value[0] == 3325):
                        msg = (3325).to_bytes(2, "big") + (value[1]).to_bytes(2, "big")
                        msg = base64.b64encode(msg)
                        msg = msg.decode('ascii')
                        publish_node(msg, node2, port_node2)
                
                f = open("logs.log", "a+")
                f.write(dt+" - Données envoyées au node\n")
                f.close()

                # Envoi à Telegram les données reçues
                create_message(dt, dev_id, values, type_value, symbol)

                # Ajout à la DB
                for value in values:
                    insert_db(dt, value)

            except ErrorType:
                f = open("logs.log", "a+")
                f.write(dt + " - ERROR backend2 : Le type d'une valeur reçue depuis le payload n'est pas valide\n")
                f.close()
            except ErrorValue:
                f = open("logs.log", "a+")
                f.write(dt + " - ERROR backend2 : Une des valeurs reçues du payload n'est pas valide\n")
                f.close()
            except:
                f = open("logs.log", "a+")
                f.write(dt + " - ERROR backend2: Erreur inconnue avec les données reçues de backend2\n")
                f.close()
    except:
        f = open("server_socket.log", "a+")
        f.write("Error Socket TCP: erreur avec le daemon socket TCP. Arrêt du socket...\n")
    finally:
        s.close()    

# Envoie des données vers nos Nodes
def publish_node(message, node, port_node):
    client.publish(app_id + "/devices/" + node + "/down", '{"port": ' + port_node + ',"confirmed": false,"payload_raw": "' + message + '"}')

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
        return True if 0.0 <= value <= 1000.0 else False
    elif(type == 3325):
        return True if 0 <= value <= 60000 else False
    else:
        raise ErrorValue

# Parser les données reçues par le payload
def parser_data(data):
    values = []

    while(data):
        # Récupère le nombre représentant le type de données et l'enlève du payload 
        type_number = int.from_bytes(data[:2], 'big')
        del data[:2]
        value = 0
        # Récupère la valeur du type et l'enlève du payload
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
    # Retourne des tuples (type, valeur)
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

            # Ecriture des informations du payload reçu dans un fichier log
            # (Datetime + Topic qui a envoyé le payload + payload entier)
            f = open("logs.log", "a+")
            f.write(dt+" - ")
            f.write(str(msg.topic)+"   ")
            f.write(str(msg.payload))
            f.write("\n")
            f.close()

            # Parser les valeurs contenues dans le payload initial
            values = parser_data(bytearray(payload_decode))

            # Vérifier chaque valeur selon leur barême
            for value in values:
                if(not check_values(value[0], value[1])):
                    raise ErrorValue

            # Envoi sur Telegram des valeurs reçues
            create_message(dt, dev_id, values, type_value, symbol)
            # Ajout des valeurs dans la DB
            for value in values:
                insert_db(dt, value)

            # Envoi des datas pour l'autre groupe
            thread = threading.Thread(target=send_data, args=(dt, payload_decode))
            thread.start()
            thread.join()
        
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

thread = threading.Thread(target=socket_server, daemon=True)
thread.start()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_log = on_log

client.username_pw_set(app_id,access_key)
client.connect("eu.thethings.network", 1883, 60)
client.loop_forever()