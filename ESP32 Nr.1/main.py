from time import sleep
from machine import ADC, Pin, SPI
import neopixel

# Variabler til SPI-forbindelse
spi = SPI(1, baudrate=10000000, polarity=0, phase=0)  # initialize SPI bus
cs = Pin(5, Pin.OUT)  # set chip select pin
cs.on() 

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
    co2_ppm = read_mq()
    print(f"CO2 Level: {co2_ppm} ppm")
    sleep(1)
    
    
    value = 42  # integer to send
    cs.off()  # select chip
    spi.write(bytearray([value]))  # send integer as a single byte
    cs.on()  # deselect chip
    sleep(1)  # wait for 1 second before sending another integer
    
    if co2_ppm <= 400:
        np_Green()
        
    elif co2_ppm <= 600:
        np_Yellow()
    
    else:
        np_Red()

