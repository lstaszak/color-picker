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
        color_name_en = color_info.find(id="uscBootStrapHeader_lblTitle").small.text.lower()
        # requests.get('https://slack.com/api/chat.postMessage?token=' + SLACK_TOKEN + '&channel=' + SLACK_CHANNEL + '&text=' + color_name_en)
    
        result = requests.get('https://www.diki.pl/slownik-angielskiego?q=' + color_name_en)
        diki_color_info = BeautifulSoup(result.content, 'html.parser')
        color_name_pl = diki_color_info.findAll('a', {'class': 'plainLink' })
        
        print(len(color_name_pl))
        
        color_name_stem = hex_color + ' ' + color_name_en
        
        if (len(color_name_pl) >= 2):
            color_name_stem = color_name_stem + ' - ' + color_name_pl[0].string + ' LUB ' + color_name_pl[1].string
        
        if (len(color_name_pl) >= 3):
            color_name_stem = color_name_stem + ' LUB ' + color_name_pl[2].string
        
        print(color_name_stem)
        
        data = {
            'hex':hex_color, 
            'color_name_en':color_name_en, 
            'color_name_pl':color_name_stem
        }
        
        db.child('colors').push(data)
        requests.get('https://slack.com/api/chat.postMessage?token=' + SLACK_TOKEN + '&channel=' + SLACK_CHANNEL + '&text=' + color_name_stem)
    
client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

client.on_connect    = connected
client.on_disconnect = disconnected
client.on_message    = message

client.connect()
client.loop_blocking()