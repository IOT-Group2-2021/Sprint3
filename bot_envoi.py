"""Envoi des messages vers Telegram"""

__author__      = "Michaël da Silva, Guillaume Schranz, Nenad Rajic, Walid Massaoudi"
__copyright__   = "Copyright 2021, HEIG-VD"
__license__ 	= "GPL"
__version__ 	= "3.0"
__email__       = "michael.dasilva@heig-vd.ch, guillaume.schranz@heig-vd.ch, nenad.rajic@heig-vd.ch, walid.massaoudi@heig-vd.ch"
__status__ 		= "Prototype"

import telegram
import mysql.connector 

#Token that can be generated talking with @BotFather on telegram
my_token = '1550755380:AAHMdqbskoBlYE-gOib34wLmu-xsEPnAgEo'
#TOKEN = '1779634406:AAF1prwgBVZti1CCO9mvBBvGVAu6uR_qwwE'
chat_id = -1001155359564

#Envoi du message à proprement parlé
def send_message(msg, id=chat_id, token=my_token):
	bot = telegram.Bot(token=token)
	bot.sendMessage(chat_id=id, text=msg)


def create_message(dt, topic, values, type_value, symbol):
    alert = ("Alert !\n\n")
    alert += ("Valeur reçue de " + str(topic) + "\n")
    
    for value in values:
        alert += (" - " + type_value[value[0]] + " = " + str(value[1]) + " " + symbol[value[0]])
        #if(values.index(value) != len(values) - 1):
        alert += ("\n")
    alert += ("Date : " + dt)
    send_message(alert)

#Information connexion base de donnée
baseDeDonnees = mysql.connector.connect(
    host="localhost",
    user="root",
    password="IOTgroup2$", 
    database="iot-group2"
)