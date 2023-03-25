from umqtt.simple import MQTTClient
from machine import ADC, Pin
from time import sleep
import _thread as thread
import neopixel
import network

# Mqtt variabler 
SERVER = 'raspberrypi.local'  # MQTT Server Addresse
CLIENT_ID = 'ESP32_MQ135_Sensor'
TOPIC = b'CO2_ppm'
client = MQTTClient(CLIENT_ID, SERVER)

# MQ135 sensor variabler
RL_VALUE = 10
RO_CLEAN_AIR_FACTOR = 9.83

# Neopixel variabler
n = 12
p = 15
np = neopixel.NeoPixel(Pin(p), n)

# Instans af ADC klassen
adc = ADC(Pin(36))
adc.atten(ADC.ATTN_11DB)

# Neopixel funktioner
def np_off():
    for i in range(12):
        np[i] = (0, 0, 0)
        np.write()

def np_Green():
    for i in range(12):
        np[i] = (0, 50, 0)
        np.write()
        
def np_Yellow():
    for i in range(12):
        np[i] = (50, 50, 0)
        np.write()
        
def np_Red():
    for i in range(12):
        np[i] = (50, 0, 0)
        np.write()

# Funktion til at læse MQ153 sensor
def read_mq():
    rs = adc.read() / 4095 * 3.3 / (5.0 - adc.read() / 4095 * 3.3) * RL_VALUE
    ratio = rs / RO_CLEAN_AIR_FACTOR
    co2_ppm = round(1.8
                    * pow(ratio, -1.769034857))
    return co2_ppm

# Funktion til tråd 1
def sensor_indikator():
    while True:
        co2_ppm = read_mq()
        print(f"CO2 Level: {co2_ppm} ppm")
        sleep(1)
        
        if co2_ppm <= 400:
            np_Green()
            
        elif co2_ppm <= 600:
            np_Yellow()
        
        else:
            np_Red()

# Funktion til tråd 2 
def mqtt_publish_til_RPI():
    while True:
        co2_ppm = read_mq()
        msg = (b'{}'.format(co2_ppm))
        client.publish(TOPIC, msg)  # Publish sensor data to MQTT topic
        print(msg)
        sleep(300)

# Opret forbindelse til MQTT broker
client.connect()   

# Sluk Neopixel
np_off()

# Start 2 nye tråde
thread.start_new_thread(sensor_indikator,())
thread.start_new_thread(mqtt_publish_til_RPI,())