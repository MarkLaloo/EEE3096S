#imports for I/O
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import RPi.GPIO as GPIO 
#imports for threading 
import threading
from datetime import datetime

#globgogabgalab vars
button = 22 #board pin 15  
sampleTime = 1 #initial sample time 
ldr = 0 #intiailise as 0
tempS = 0 #intiailise as 0
startTime = 0 #intiailise as 0
runTime = 0 #intiailise as 0


def setup():
    # button nonsense
    GPIO.setmode(GPIO.BCM) #setup boardmode 
    GPIO.setup(button,GPIO.IN,pull_up_down = GPIO.PUD_UP) #setup button for pullup input mode
    #interrupt and debouncing 
    GPIO.add_event_detect(button, GPIO.FALLING, callback=changeSampleTime, bouncetime=200)

    #ADC nonsense 
    # create the spi bus
    spi = busio.SPI(clock = board.SCK, MISO = board.MISO , MOSI = board.MOSI) 
    #create the chip select (cs)
    cs = digitalio.DigitalInOut(board.D5)
    #create the MCP objects
    mcp = MCP.MCP3008(spi, cs)
    # create an analog input channel on pins 2 and 3 (channels 1 and 2 respectively)
    global ldr,tempS,startTime
    startTime = datetime.now()
    ldr = AnalogIn(mcp, MCP.P2) #ldr on pin 3 / channel 2
    tempS = AnalogIn(mcp, MCP.P1) #temp sensor on pin 2 / channel 1

    #print header
    print("{:<10} {:<15} {:<15} {:<10} {:<15}".format('Runtime','Temp Reading','Temp','','Light Reading')) #fancy ooo


def changeSampleTime(channel):
    global sampleTime
    if sampleTime == 1:
        sampleTime = 5
    elif sampleTime == 5:
        sampleTime = 10 
    elif sampleTime == 10:
        sampleTime = 1
    #print('time =', sampleTime)
    pass

def timedThread():
    global ldr,tempS,runTime,startTime
    thread = threading.Timer(sampleTime,timedThread)
    thread.daemon = True
    thread.start()
   

    end=datetime.now()
    dur = end - startTime
    dur = dur.seconds
    startTime=end
    runTime+=dur

    #voltage-0.5 bc 0deg Celsius at 500mV according to the datasheet
    #thereafter is linear where 10mV=1deg celsius so x100 converts to temp
    temp = (tempS.voltage-0.5)*100    

    print("{:<10} {:<15} {:<15} {:<10} {:<15}".format(str(runTime)+'s',str(tempS.value),str(temp)[:10],'C',str(ldr.value))) #fancy ooo

    #eternal print statements for sensor checking
    #unccomment these for debugging 
    #print('Raw ADC Value (LDR):', ldr.value)
    #print('ADC Voltage(LDR):'  + str(ldr.voltage) + 'V')
    #print('Raw ADC Value (TEMP):', temp.value)
    #print('ADC Voltage(TEMP):'  + str(temp.voltage) + 'V')
    #print("Temperature =", (temp.voltage - 0.5)*100)
    pass


if __name__ == '__main__':
    try:
        setup()
        timedThread()
        while True:
            pass
    finally:
        GPIO.cleanup() 
