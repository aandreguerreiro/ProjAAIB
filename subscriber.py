import paho.mqtt.client as mqtt
import threading
import time
import time

RATE = 44100

broker="test.mosquitto.org"
port=1883
topic = "AAIB"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
    else:
        print("Connection failed")
        
    client.subscribe(topic)
    print("subscribing to topic : " + topic)


def disconnect():
    print("client is disconnecting..")
    client.disconnect()


def on_message(client, userdata, message):
    data = message.payload.decode('utf-8')
    print("received message: " ,str(data))
    with open('/workspace/ProjAAIB/sounddata.txt', 'a', encoding='UTF8') as f:
        f.write(data + "\n")
    time.sleep(1/RATE) 
    

client = mqtt.Client()
client.connect(broker, port) 
client.on_connect= on_connect

def subscribing():
    client.on_message = on_message
    client.loop_forever()


sub=threading.Thread(target=subscribing)

sub.start()
