#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Backend pour le projet IOT"""

__author__      = "Michaël da Silva, Guillaume Schranz, Nenad Rajic, Walid Massaoudi"
__copyright__   = "Copyright 2021, HEIG-VD"
__license__ 	= "GPL"
__version__ 	= "3.0"
__email__       = "michael.dasilva@heig-vd.ch, guillaume.schranz@heig-vd.ch, nenad.rajic@heig-vd.ch, walid.massaoudi@heig-vd.ch"
__status__ 		= "Prototype"

#import paho.mqtt.client as mqtt
import base64
import datetime
import socket
#import mysql.connector

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
"""

type = {3302: "presence", 3303: "temperature", 3304: "rh", 3315: "pressure", 3324: "loudness", 3325: "concentration"}
unit = {3302: "", 3303: "°C", 3304: "%", 3315: "hPa", 3324: "mV", 3325: "ppm"}

def parser_data(data):
    while(data):
        type_number = data[:2]
        del data[:2]
        type_ = type.get(type_number)
        unit_ = unit.get(type_number)

data = (3303).to_bytes(2, 'big') + (327).to_bytes(2, 'big')
parser_data(data)