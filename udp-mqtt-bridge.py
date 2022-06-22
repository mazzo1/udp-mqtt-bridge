import paho.mqtt.client as mqtt
import socket
import threading
import collections

from collections import namedtuple
from bridge_config import *
from time import sleep

version = 1.7

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDPMessage = namedtuple('udp_message', {'type':'', 'target':'', 'entity':'', 'param':[], 'auth':''})

class UDP_thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.UDP_PORT = UDP_PORT
        sock.bind((SELF_CLIENT.ipv4, self.UDP_PORT))

    def run(self):
        while True:
            data, addr = sock.recvfrom(1024)
            data_str = data.decode('utf-8')
            print(f"[ UDP SERVICE ]: Received message {data_str}")

            process_message(data=data)

    def fire_udp(self, payload, target):
        payload = bytes(payload, 'utf-8')

        if SELF_CLIENT.nickname in payload.decode('utf-8').split('_'):
            print('nice try')
            return False

        try:
            HOSTNAME_TARGET, IP_TARGET = search_name_table(target)
        except:
            print("!!! Error: Could not find target in database")

        if HOSTNAME_TARGET:
            sock.sendto(payload, (HOSTNAME_TARGET, UDP_PORT))
            print(f"[ UDP SERVICE ]: Message forwarded to {HOSTNAME_TARGET}")
            return True

def process_message(data=None, parsed_msg=None):
    """Function for processing incoming message, determining what it is, and what to do with it"""
    if not parsed_msg:
        parsed_msg, rebuilt_msg = parse_msg(data, 1)
#    print(parsed_msg)
    if parsed_msg.type == 'U2':
        U2_handler(parsed_msg)

    if "4WHEELER" in parsed_msg:
        topic = '4wheeler/status'

    if parsed_msg.target == 'CASH':
        fire_mqtt(rebuilt_msg, topic)

#    if parsed_msg.target == SELF_CLIENT.nickname:
#        print("That's for me!!")

    try:
        assert(int(parsed_msg.auth) > 0)
        assert(parsed_msg.target != SELF_CLIENT.nickname)
        UDP.fire_udp(rebuilt_msg, parsed_msg.target)
    except:
        return False
        print("[ UDP SERVICE ]: Could not validate ")



def U2_handler(parsed_msg):
    global CONNECTED

    try:
        assert(parsed_msg.target)
    except:
        print("!!! Error: no target")

    try:
        assert(parsed_msg.entity)
    except:
        print("!!! Error: no entity")

    try:
        assert(parsed_msg.param[0])
    except:
        print("!!! Error: no parameters")

    else:

        if parsed_msg.target == SELF_CLIENT.nickname:
            if parsed_msg.entity == 'CASH':
                if parsed_msg.param[0] == "OK":
                    CONNECTED = True
                    print(f"[ MQTT CLIENT ]: {SELF_CLIENT.nickname} online!")

    '''finally:
        if parsed_msg.target == "CASH":
            try:
                HOSTNAME_TARGET, IP_TARGET = search_name_table(parsed_msg.target)
            except:
                print("!!! Error: Could not find target in database")

            fire_mqtt(
            '''
def parse_msg(msg, translate=0):

    try:
        parsed = (msg).decode('utf-8').split("_")
    except:
        print("!!! Error decoding bytes message to string")

    try:
        UDP_MSG_TYPE = parsed.pop(0)
    except:
        UDP_MSG_TYPE = "U0"
        print("!!! Error parsing message type")

    try:
        UDP_MSG_TARGET = parsed.pop(0)
    except:
        UDP_MSG_TARGET = ''
        print("!!! Error parsing target")

    try:
        UDP_MSG_ENTITY = parsed.pop(0)
    except:
        UDP_MSG_ENTITY = ''
        print("!!! Error parsing entity")

    try:
        UDP_MSG_AUTH = parsed.pop(-1).split("*")[1]
        assert(int(UDP_MSG_AUTH))
    except:
        UDP_MSG_AUTH = 0
        print("!!! Error parsing AUTH code")

    try:
        UDP_MSG_PARAMETERS = parsed
    except:
        UDP_MSG_PARAMETERS = ''
        print("!!! Error parsing parameters")

    try:
        REBUILT_UDP_MSG = f"{UDP_MSG_TYPE}_{UDP_MSG_TARGET}_{UDP_MSG_ENTITY}_"
    except:
        print("!!! Error rebuilding UDP message")

    try:

        for i in UDP_MSG_PARAMETERS:
            REBUILT_UDP_MSG += i+"_"
    except:
        print("!!! Error attaching parameters to rebuilt UDP message")

    try:
        REBUILT_UDP_MSG += "*"+UDP_MSG_AUTH
    except:
        print("!!! NOT AUTHORIZED !!! \n!!! Cannot authenticate message")

    UDP_nt_obj = UDPMessage(UDP_MSG_TYPE, UDP_MSG_TARGET, UDP_MSG_ENTITY, UDP_MSG_PARAMETERS, UDP_MSG_AUTH)


    if translate:
        return UDP_nt_obj, REBUILT_UDP_MSG
    else:
        return UDP_nt_obj

def fire_mqtt(msg, topic=None):
    if topic == None:
        topic = "home/client_status"
    client.publish(topic, payload=msg)
    print(f"[ MQTT CLIENT ](pub): {msg} fired on topic: {topic}")
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    pass
  
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(f"\n[ MQTT CLIENT ](sub): {msg.payload} on topic: {msg.topic}")

    try:
        Parsed_msg, rebuilt_msg = parse_msg(msg.payload, 1)
        assert(Parsed_msg.target != None)
        if SELF_CLIENT.nickname not in Parsed_msg:
            UDP.fire_udp(rebuilt_msg, Parsed_msg.target)
        else:
            print("[ MQTT CLIENT ]: ignoring")
            process_message(parsed_msg=Parsed_msg)

    except Exception as e:
        print(f"!!! Error parsing MQTT message: {e}")


client = mqtt.Client(client_id=str(SELF_CLIENT.nickname))
client.on_connect = on_connect
client.on_message = on_message


CONNECTED = False


while not CONNECTED:

    client.connect(MQTT_BROKER_IP)
    client.subscribe("home/#")
    client.loop_start()

    msg_payload = f"U1_CASH_{SELF_CLIENT.nickname}_ONLINE_*1"
    result = client.publish("home/client_status", payload=msg_payload)
    print("[ SERVER ]: Waiting for CASH Birth Acknowledgement...")

    sleep(BIRTH_ACK_TIME)

    if CONNECTED:
        break
    else:
         client.loop_stop()

UDP = UDP_thread()
UDP.start()


while CONNECTED:
    sleep(1)
    pass

UDP.join()
client.loop_stop()
