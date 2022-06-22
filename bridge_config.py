#config file for bridge server
import collections
from collections import namedtuple

ClientDNK = namedtuple('donkey_client', ('nickname', 'hostname', 'ipv4', 'topic'), defaults=(None, None, None, 'home/client_status'))
 

# List of authorized clients on Donkey network
#####################################################################################
DNK_BLITZ = ClientDNK('BLITZ', 'blitz.local', '192.168.100.31')
DNK_GARAGE = ClientDNK('GARAGE', 'garage-opener-switch.local', '192.168.100.95')
DNK_RFIDGARAGE = ClientDNK('RFIDGARAGE', 'garage-rfid-reader.local', '192.168.100.96')
DNK_HAMMOODYMAIN = ClientDNK('HAMMOODYMAIN', 'HammoodyMain.local', '192.168.100.66')
DNK_CASH = ClientDNK('CASH', 'cash.local', '192.168.100.32')
DNK_DONKEY = ClientDNK('DONKEY', 'donkey.local', '192.168.100.1') #potential security concern to have default gateway exposed.. or is it?
DNK_MOHOMBP = ClientDNK('MOHOMBP', 'MOHOMBP.local', '192.168.100.70')
DNK_MOHOIPHONE = ClientDNK('MOHOIPHONE', 'Mohamads-iPhone.local', '192.168.100.69')
DNK_4WHEELER = ClientDNK('4WHEELER', '4wheeler.local', '192.168.100.77', '4wheeler/status')
#####################################################################################

# probably don't change these
SELF_CLIENT = DNK_BLITZ # under normal operation, this should be DNK_BLITZ
MQTT_BROKER_IP = DNK_CASH.hostname # under normal operation, this should be DNK_CASH.ipv4
topic = 'home/client_status' # default 
UDP_PORT = 5005 # normally 5005
BIRTH_ACK_TIME = 2 #time to wait for broker acknowledgement reply of client going online, normally 2

#list of registered clients. only modify when modifying the list of DNK_Clients up above ^^^
names = [
DNK_DONKEY,
DNK_CASH,
DNK_BLITZ,
DNK_GARAGE,
DNK_RFIDGARAGE,
DNK_HAMMOODYMAIN,
DNK_MOHOMBP,
DNK_4WHEELER
]


# function for main script to index sendable address for target machine
def search_name_table(target):
	for i in names:
		if i.nickname == target:
			return i.hostname, i.ipv4
