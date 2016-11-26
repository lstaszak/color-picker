# Author: Lukasz Staszak

import random
import sys
import time
import requests
from Adafruit_IO import MQTTClient
from bs4 import BeautifulSoup

ADAFRUIT_IO_KEY      = '7be3825298fc414091a5ca2890429789'
ADAFRUIT_IO_USERNAME = 'lstaszak'

SLACK_TOKEN          = 'xoxp-3391670007-3391670021-40756783332-74f518c249'
SLACK_CHANNEL        = 'C35G97DGD'

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
    color_name = color_info.find(id="uscBootStrapHeader_lblTitle").small.text
    
    requests.get('https://slack.com/api/chat.postMessage?token=' + SLACK_TOKEN + '&channel=' + SLACK_CHANNEL + '&text=' + color_name)

client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

client.on_connect    = connected
client.on_disconnect = disconnected
client.on_message    = message

client.connect()
client.loop_blocking()