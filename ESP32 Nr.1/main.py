from time import sleep
from machine import ADC, Pin, UART
import neopixel

# Variabler til UART-forbindelse
uart = UART(2, baudrate=115200, tx=1, rx=3)

# Set up the MQ135 sensor
RL_VALUE = 10
RO_CLEAN_AIR_FACTOR = 9.83

# Variabler til neopixel ring
n = 12
p = 15
np = neopixel.NeoPixel(Pin(p), n)

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
        
adc = ADC(Pin(36))
adc.atten(ADC.ATTN_11DB)

def read_mq():
    rs = adc.read() / 4095 * 3.3 / (5.0 - adc.read() / 4095 * 3.3) * RL_VALUE
    ratio = rs / RO_CLEAN_AIR_FACTOR
    co2_ppm = round(2.9820682 * pow(ratio, -1.769034857))
    return co2_ppm

np_off()

while True:
    co2_ppm_read = read_mq()
    print("CO2 Level: {} ppm".format(co2_ppm_read))
    sleep(1)
    
    my_bytes = bytes([co2_ppm_read])
    
    UART.write(my_bytes)
    
    if co2_ppm_read <= 400:
        np_Green()
        
    elif co2_ppm_read <= 600:
        np_Yellow()
    
    else:
        np_Red()

