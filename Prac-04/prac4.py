import busio
import digitalio
import board
import threading
from datetime import datetime
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
#import RPi.GPIO as GPIO
#tried to setup nicely using function blocks

btn = 18

def setup():
    # create the spi bus
    #GPIO.setmode(GPIO.BOARD)
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

    # create the cs (chip select)
    cs = digitalio.DigitalInOut(board.D5)

    # crate the mcp object
    global mcp
    mcp = MCP.MCP3008(spi, cs)
    
    global sampleTime
    sampleTime = 5
    print("{:<10} {:<15} {:<15} {:<10} {:<15}".format('Runtime','Temp Reading','Temp','','Light Reading')) #nice format
    
    #below is button setup, not complete
    btn=digitalio.DigitalInOut(board.D18)
    btn.direction = digitalio.Direction.INPUT
    btn.pull = digitalio.Pull.UP
    #to change time, not yet used, relies on btn 
    if btn.value == False:
        change_sample_time()

    global start
    start=datetime.now()
    # create an analog input channel on pin 0



def change_sample_time():
    #cycles sample time
    global sampleTime
    if sampleTime==1:
        sampleTime=5
    elif sampleTime==5:
        sampleTime=10
    elif sampleTime==10:
        sampleTime=1

def print_thread():


    thread = threading.Timer(sampleTime,print_thread)
    thread.daemon = True
    
    global start
    end=datetime.now()
    dur = end - start
    dur = dur.seconds
    start=end

    thread.start()
    

    tempSens = AnalogIn(mcp, MCP.P1)
    LDR = AnalogIn(mcp,MCP.P2)

    #voltage-0.5 bc 0deg Celsius at 500mV according to the datasheet
    #thereafter is linear where 10mV=1deg celsius so x100 converts to temp
    temp = (tempSens.voltage-0.5)*100    

    #print('Raw ADC tempSens Value: ', tempSens.value)
    #print('tempSens ADC Voltage: '+str(tempSens.voltage) + 'V')
    #print('The Temperature is currently '+str(temp)+'C')
    
    #print('Raw ADC LDR Value: ', LDR.value)
    #print('LDR ADC Voltage: '+str(LDR.voltage))
    print("{:<10} {:<15} {:<15} {:<10} {:<15}".format(str(dur),str(tempSens.value),str(temp)[:10],'C',str(LDR.value))) # fancy print
    

    

if __name__ == "__main__":
    setup()
    print_thread()
    while True:
        pass

