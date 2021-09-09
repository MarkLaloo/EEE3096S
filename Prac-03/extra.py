import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils

eeprom = ES2EEPROMUtils.ES2EEPROM()



def test():
    eeprom.clear(1024)
    data=input("input:")
    arr=[]
    for i in range(0,len(data)):
        if i<3:
            arr.append(ord(data[i]))
    #print(arr)
    eeprom.write_block(1,arr)
    print('test')
    #print(getScore(1))
    #print('test1')
    #print(eeprom.read_block(1,4))
    temp=getScore(1)
    print(temp)

def getScore(blockNum):
    name=''
    blockData=eeprom.read_block(blockNum,4)
    for i in range(0,3):
        letter=chr(blockData[i])
        name=name+letter
    score = blockData[3]
    output=[name,score]
    return output



if __name__ == "__main__":
    try:
        # Call setup function
        test()
    except Exception as e:
        print(e)
