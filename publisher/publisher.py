import paho.mqtt.client as mqtt 
import time
import pyaudio
import audioop
import threading

client = mqtt.Client()
broker="test.mosquitto.org"
port=1883
topic="AAIB"

def on_connect(client, userdata, flags, rc):

    if rc == 0:
        print("Connected to broker")
    else:
        print("Connection failed")
    client.subscribe("Status")
    print("subscribing to topic : " + "Status")
    
    
def disconnect():
    print("client is disconnecting..")
    client.disconnect()
    print("client is disconnecting..")
    


def on_message(client, userdata, message):
    global stop_threads
    msg = message.payload.decode("utf-8")
    
    if msg == "False":
        stop_threads = True
        disconnect()
        pub.join()
        
    if msg == "True":
        stop_threads = False
        pub.start()
        
        


def main():
    p = pyaudio.PyAudio()
    
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
     

    stream = p.open(format=FORMAT, input_device_index=1,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    
    print("*recording*")
    
    while True:
        global stop_threads
        
        if stop_threads:
            break
        else:
            data = stream.read(CHUNK)
            rms = audioop.rms(data, 2)
            client.publish(topic, rms)
            time.sleep(1/RATE)
    
    print("*done recording*")
    stream.stop_stream()
    stream.close()
    p.terminate()
            

client.connect(broker, port) 
client.on_connect= on_connect

def subscribing():
    
    client.on_message = on_message
    client.loop_forever()

sub=threading.Thread(target=subscribing)
pub=threading.Thread(target=main)

stop_threads = False
sub.start()