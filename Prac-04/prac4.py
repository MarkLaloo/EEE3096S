import busio
import digitalio
import board
import threading
from datetime import datetime
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
#import gpiozero
import RPi.GPIO as GPIO
#tried to setup nicely using function blocks

btn = 24
totalDur=0

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(btn,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(btn,GPIO.RISING,callback=change_sample_time,bouncetime=200)

    # create the spi bus
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

    # create the cs (chip select)
    cs = digitalio.DigitalInOut(board.D5)

    # crate the mcp object
    global mcp
    mcp = MCP.MCP3008(spi, cs)
    
    global sampleTime
    sampleTime = 1
    print("{:<10} {:<15} {:<15} {:<10} {:<15}".format('Runtime','Temp Reading','Temp','','Light Reading')) #nice format
    
    #below is button setup, not complete
    #btn=digitalio.DigitalInOut(board.D18)
    #btn.direction = digitalio.Direction.INPUT
    #btn.pull = digitalio.Pull.UP
    #to change time, not yet used, relies on btn 
    #btn = gpiozero.Button(24)
    #btn.when_pressed = change_sample_time
    
    global start
    start=datetime.now()
    # create an analog input channel on pin 0



def change_sample_time(channel):
    #cycles sample time
    #print('sample time changed')
    global sampleTime
    if sampleTime==1:
        sampleTime=5
    elif sampleTime==5:
        sampleTime=10
    elif sampleTime==10:
        sampleTime=1
    #print('sample time = ',sampleTime)

def print_thread():
    #global btn
    #btn.when_pressed = change_sample_time

    thread = threading.Timer(sampleTime,print_thread)
    thread.daemon = True
    
    global start
    global totalDur
    end=datetime.now()
    dur = end - start
    dur = dur.seconds
    start=end
    totalDur+=dur
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
    print("{:<10} {:<15} {:<15} {:<10} {:<15}".format(str(totalDur)+'s',str(tempSens.value),str(temp)[:10],'C',str(LDR.value))) # fancy print
    
    

if __name__ == "__main__":
    setup()
    print_thread()
    while True:
        pass

