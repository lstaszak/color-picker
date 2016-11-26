# Author: Lukasz Staszak

import random
import sys
import time
import requests
import urllib3
import pyrebase
from Adafruit_IO import MQTTClient
from bs4 import BeautifulSoup

ADAFRUIT_IO_KEY      = '7be3825298fc414091a5ca2890429789'
ADAFRUIT_IO_USERNAME = 'lstaszak'

SLACK_TOKEN          = 'xoxp-3391670007-3391670021-40756783332-74f518c249'
SLACK_CHANNEL        = 'C35G97DGD'

config = {
    "apiKey": "AIzaSyD5p3sQxRPjiBUpNkHYwcQkgJ1kRmr9tDc",
    "authDomain": "colorpicker-7ee2b.firebaseapp.com",
    "databaseURL": "https://colorpicker-7ee2b.firebaseio.com",
    "storageBucket": "colorpicker-7ee2b.appspot.com",
    "messagingSenderId": "606374990628"
}

firebase = pyrebase.initialize_app(config)

db = firebase.database()

def connected(client):
    print 'Connected to Adafruit IO!  Listening for color-picker changes...'
    client.subscribe('color-picker')

def disconnected(client):
    print 'Disconnected from Adafruit IO!'
    sys.exit(1)

def message(client, feed_id, payload):
    print 'Feed {0} received new value: {1}'.format(feed_id, payload)
    
    hex_color = payload.replace('#', '');
    result = requests.get('http://www.htmlcsscolor.com/hex/' + hex_color)
    
    content = result.content
    color_info = BeautifulSoup(content, 'html.parser')
    color_name_en = color_info.find(id="uscBootStrapHeader_lblTitle").small
    
    if color_name_en: 
        color_name_en = color_name_en.text.lower()
        for color_name_en_val in color_name_en.split():
            print(color_name_en_val)
            result = requests.get('https://www.diki.pl/slownik-angielskiego?q=' + color_name_en_val)
            diki_color_info = BeautifulSoup(result.content, 'html.parser')
            color_name_pl = diki_color_info.findAll('span', {'class':'partOfSpeech'})
            type_p = []
            type_r = []
            for color_name_pl_val in color_name_pl:
                if color_name_pl_val.string == 'przymiotnik':
                    if color_name_pl_val.parent is not None and len(color_name_pl_val.parent) != 0:
                        if color_name_pl_val.parent.findNext('ol') is not None and len(color_name_pl_val.parent.findNext('ol')) != 0:
                            for x in color_name_pl_val.parent.findNext('ol').find('span', {'class':'hw'}):
                                type_p.append(x.string)
                if color_name_pl_val.string == 'rzeczownik':
                    if color_name_pl_val.parent is not None and len(color_name_pl_val.parent) != 0:
                        if color_name_pl_val.parent.findNext('ol') is not None and len(color_name_pl_val.parent.findNext('ol')) != 0:
                            for x in color_name_pl_val.parent.findNext('ol').find('span', {'class':'hw'}):
                                type_r.append(x.string)
        data = {
            'hex':hex_color, 
            'color_name_en':color_name_en, 
            'color_name_pl_type_p':type_p,
            'color_name_pl_type_r':type_r
        }
        
        print(data)
        db.child('colors').push(data)

client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

client.on_connect    = connected
client.on_disconnect = disconnected
client.on_message    = message

client.connect()
client.loop_blocking()