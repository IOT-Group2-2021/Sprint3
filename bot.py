#!/usr/bin/env python

"""bot pour le projet IOT"""

__author__      = "Michaël da Silva, Guillaume Schranz, Nenad Rajic, Walid Massaoudi"
__copyright__   = "Copyright 2021, HEIG-VD"
__license__ 	= "GPL"
__version__ 	= "3.0"
__email__       = "michael.dasilva@heig-vd.ch, guillaume.schranz@heig-vd.ch, nenad.rajic@heig-vd.ch, walid.massaoudi@heig-vd.ch"
__status__ 		= "Prototype"

import base64

#on relie notre bot à telegrame avec la classe Updater
from telegram.ext import Updater
#le dispatcher permet de répondre à ce qui se passe dans le channel
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

#no spam
TOKEN = '1550755380:AAHMdqbskoBlYE-gOib34wLmu-xsEPnAgEo' 

#Attention à traiter les overflows en cas de grosses valeurs 
MIN_FREQU = 30000 #30 secondes
MAX_FREQU = 60000 #1 minutes

def convert_to_base64(value):
    base64_message = base64.b64encode(value.to_bytes(2, "big"))
    return base64_message

def is_int(value):
    try:
        return int(value)
    except:
        return False

def is_valid_freq(value):
    return value >= MIN_FREQU and value <= MAX_FREQU
        

def test(update, context):
    update.message.reply_text("message recu")

def pas_compris(update, context):
    mess = 'La commande suivante n\'existe pas : '+ update.message.text
    print(mess)
    update.message.reply_text(mess)

def help(update, context):
    message="Bonjour, voici les commandes disponibles : \n - /help\n - /freq + int\n - /test"
    context.bot.send_message(chat_id=update.message.chat_id, text=message)

def freq(update, context):
    #vérification qu'un paramètre soit passé à la fonction freq
    if len(context.args) != 0:
        message = context.args[0]
    else:
        message = "error"

    #initialisation à une valeur nulle, permet d'éviter un encodage sur des valeurs non valide ensuite
    message_base64 = base64.b64encode("".encode())
    text_valid = ""

    #Vérification si la valeur entrée est effectivemetn entière
    numeric_val = is_int(message)

    #on encode puis publish uniquement si le message est un int et qu'il se trouvent entre les bornes
    if (numeric_val):
        print("is int ? YES")
        if is_valid_freq(numeric_val):
            print("is valid ? YES")
            text_valid = "la valeur est valide"
            message_base64 = convert_to_base64(int(message))
            #envoi du message à TTN
            #publish_node(message_base64.decode('ascii'), "intrusiondetector", "1")
        else:
            print("is valid ? no")
            text_valid = "La frequence entrée n'est pas valide (MIN : " + str(MIN_FREQU) + " MAX : " + str(MAX_FREQU) + ")"
    else:
        print("is int ? NOP")
        text_valid = "Utilisation de freq : /freq (valeur entière)"

    #Préparation du string à envoyer au front end
    message_to_send = "Valeur entrée : " + message + "\nValeur en base 64 : " + message_base64.decode('ascii') + "\n" + text_valid
    
    #envoi au front end
    context.bot.send_message(chat_id=update.message.chat_id, text="fonction frequence !\n" + message_to_send)
    

def botRunning():
    #permet de lire en continu ce qui se passe sur le channel
    updater = Updater(TOKEN, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('freq', freq, pass_args=True))

    updater.dispatcher.add_handler(CommandHandler("test", test))
    
    updater.dispatcher.add_handler(CommandHandler("help", help))


    #Pour tout autre message, on utilise la fonction "pas compris"
    updater.dispatcher.add_handler(MessageHandler(Filters.text, pas_compris))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    botRunning()


