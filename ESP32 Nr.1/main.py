from umqtt.simple import MQTTClient
from machine import I2C, Pin
import _thread as thread
from time import sleep
import neopixel


# Mqtt variabler 
SERVER = 'raspberrypi.local'  # MQTT Server Addresse
CLIENT_ID = 'ESP32_MQ135_Sensor'
TOPIC = b'CO2_ppm'
client = MQTTClient(CLIENT_ID, SERVER)

# Neopixel variabler
n = 12
p = 15
np = neopixel.NeoPixel(Pin(p), n)

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

# Initialize I2C bus
i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000)
address = 0x49

# Function to read ADC data from MCP3021
def read_adc():
    data = bytearray(2)
    i2c.writeto(address, bytes([0x68]))
    i2c.readfrom_into(address, data)
    adc = ((data[0] & 0x0F) << 8) | data[1]
    return adc

# Function to convert ADC data to CO2 concentration in ppm
def adc_to_ppm(adc):
    ADC_0 = 300  # Replace with your sensor's values
    ADC_400 = 1700
    ADC_10000 = 4095
    ppm_400 = 400
    ppm_10000 = 10000
    ppm = round((adc - ADC_0) * (ppm_10000 - ppm_400) / (ADC_10000 - ADC_400) + ppm_400)
    return ppm

# Funktion til tråd 1   
def sensor_indikator():
    while True:
        adc_value = read_adc()
        co2_ppm = adc_to_ppm(adc_value)
        print(f"CO2 Level: {co2_ppm} ppm")
        sleep(1)
            
        if co2_ppm <= 500:
            np_Green()
                
        elif co2_ppm <= 800:
            np_Yellow()
            
        else:
            np_Red()
            
# Funktion til tråd 2        
def mqtt_publish_til_RPI():
    while True:
        adc_value = read_adc()
        co2_ppm = adc_to_ppm(adc_value)
        msg = (b'{}'.format(co2_ppm))
        client.publish(TOPIC, msg)  # Publish sensor data to MQTT topic
        print(msg)
        sleep(30)
        
# Opret forbindelse til MQTT broker
client.connect()   

# Sluk Neopixel
np_off()

# Start 2 nye tråde
thread.start_new_thread(sensor_indikator,())
thread.start_new_thread(mqtt_publish_til_RPI,())
