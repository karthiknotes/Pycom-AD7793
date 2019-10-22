from machine import SPI
from machine import Pin
from time import sleep
import math

STATUS_REG = [0x40]
CONFIG_WRITE_REG = [0x10]
CONFIG_READ_REG = [0x50]
ID_REG = [0x60]
MODE_WRITE_REG = [0x08]
ADC_READ_REG =[0x58]
IO_READ_REG = [0x68]
IO_WRITE_REG = [0x28]
RESET = [0xFF, 0XFF, 0XFF, 0XFF]


MD  =[0x00, 0x0A]  #   16 bit Mode register [MSB[8], LSB[8]]   Page 15 of Datasheet 
CFW =[0x00, 0x80]   #   16 bit Configuration register [MSB[8], LSB[8]] 
VREF = 1.17 # Internal V reference 1.17V, or external reference voltage                                              
GAIN = 1  # Change this according to the gain set in the Configuration register
IO =[0x00]		# 8 bit IO register to configure excitation currents to IO pins	

CS_HIGH = 1
CS_LOW =0

SPI_CS   = 'P9'
spi_cs = Pin(SPI_CS, mode = Pin.OUT)
spi_cs.value(1)
# configure the SPI master @ 2MHz
# this uses the SPI default pins for CLK, MOSI and MISO (``P10``, ``P11`` and ``P14``)
spi = SPI(0, mode=SPI.MASTER, baudrate=50000, polarity=1, phase=1, bits=8, firstbit=SPI.MSB)


def round_up(n, decimals=0):
   multiplier = 10 ** decimals
   return math.ceil(n * multiplier) / multiplier


# Reset the ADC
spi_cs.value(0)
spi.write(bytes(RESET)) # send 5 bytes on the bus
print(spi.read(4)) # receive 4 bytes on the bus
spi_cs.value(1)

# Identify the ADC
spi_cs.value(0)
spi.write(bytes(ID_REG)) # send 5 bytes on the bus
print((spi.read(1))) # receive 5 bytes on the bus
spi_cs.value(1)

#Read the ADC status
spi_cs.value(0)
spi.write(bytes(STATUS_REG)) # send 5 bytes on the bus
print((spi.read(1))) # receive 5 bytes on the bus
spi_cs.value(1)

#Set the Mode register
spi_cs.value(CS_LOW) 
spi.write(bytes(MODE_WRITE_REG))
spi.write(bytes(MD)) 
print("MODE",spi.read(2))
spi_cs.value(CS_HIGH)

#Set the Configuration register
spi_cs.value(CS_LOW)
spi.write(bytes(CONFIG_WRITE_REG))
spi.write(bytes(CFW))
print("CONFIG",spi.read(2))
spi_cs.value(CS_HIGH)

# Set the IO register
spi_cs.value(CS_LOW)
spi.write(bytes(IO_WRITE_REG))
spi.write(bytes(IO))
print("IO",spi.read(1))
spi_cs.value(CS_HIGH)

#Continuously read the voltage reading
while True:
    spi_cs.value(CS_LOW)  
    spi.write(bytes(ADC_READ_REG))
    DATA = spi.read(3)
    spi_cs.value(CS_HIGH)

    V1= ((int((DATA[0]<<16)|(DATA[1]<<8)|(DATA[2]))) - (2**(24-1)))/(2**(24-1))* (VREF/GAIN)      
    print ("Voltage = ", round_up(V1,4), "V") # rounding up the voltage to 4 decimal points
    sleep(1)
