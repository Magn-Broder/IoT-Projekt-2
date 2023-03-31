#!/home/magn3442/Project/IoT2 python3
import paho.mqtt.client as mqtt
import sqlite3
import time

db_name = 'sensor_data.db'

# log sensor data on database
def log_data(ppms):

	conn=sqlite3.connect(db_name)
	curs=conn.cursor()
	curs.execute("INSERT INTO MQ135_data values(datetime('now'), (?))", (ppms,))
	conn.commit()
	conn.close()

def on_connect(client, userdata, flags, rc):
    print('Connected with result code {0}'.format(rc))
    # Subscribe (or renew if reconnect).
    client.subscribe('CO2_ppm')

# Callback fires when a published message is received.
def on_message(client, userdata, msg):
	# Decode temperature and humidity values from binary message paylod.
	ppm = [float(x) for x in msg.payload.decode("utf-8").split(',')]
	# print('{0} ppm'.format(ppm))
	ppms = ppm[0]
	ppm_int = int(ppms)
	# print(ppm_int)
	log_data(ppm_int)
    
client = mqtt.Client()
client.on_connect = on_connect  # Specify on_connect callback
client.on_message = on_message  # Specify on_message callback
client.connect('localhost', 1883, 60)  # Connect to MQTT broker (also running on Pi).

# Processes MQTT network traffic, callbacks and reconnections. (Blocking)
client.loop_forever()

# Processes MQTT network traffic, callbacks and reconnections. (Blocking)
client.loop_forever()
