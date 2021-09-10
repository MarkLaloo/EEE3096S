# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import time
#from math import ceil
from time import sleep

# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game

# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = 33
eeprom = ES2EEPROMUtils.ES2EEPROM()
currBlock=0

lastInterruptTime = 0
currentGuess = 0

led_duty = 0
value = None
hold = 0
playerName=None
playerScore=0


 
# Print the game banner
def welcome():
    os.system('clear')
    print("  _   _                 _                  _____ _            __  __ _")
    print("| \ | |               | |                / ____| |          / _|/ _| |")
    print("|  \| |_   _ _ __ ___ | |__   ___ _ __  | (___ | |__  _   _| |_| |_| | ___ ")
    print("| . ` | | | | '_ ` _ \| '_ \ / _ \ '__|  \___ \| '_ \| | | |  _|  _| |/ _ \\")
    print("| |\  | |_| | | | | | | |_) |  __/ |     ____) | | | | |_| | | | | | |  __/")
    print("|_| \_|\__,_|_| |_| |_|_.__/ \___|_|    |_____/|_| |_|\__,_|_| |_| |_|\___|")
    print("")
    print("Guess the number and immortalise your name in the High Score Hall of Fame!")
    eeprom.clear(2048)
    sleep(0.01)
    eeprom.populate_mock_scores()
    sleep(0.01)
    eeprom.write_byte(0,4)
    sleep(0.01)

# Print the game menu
def menu():
    global end_of_game
    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()
    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
    elif option == "P":
        os.system('clear')
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        global value
        value = generate_number()
        while not end_of_game:
            pass
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    print("There are {} scores. Here are the top 3!".format(count))
    raw_data.sort(key=lambda x: x[1])
    u1 = raw_data[0]
    u2 = raw_data[1]
    u3 = raw_data[2]
    print('1 - '+u1[0]+' took '+str(u1[1])+' guesses')
    print('2 - '+u2[0]+' took '+str(u2[1])+' guesses')
    print('3 - '+u3[0]+' took '+str(u3[1])+' guesses')
    menu()
    # print out the scores in the required format
    pass


# Setup Pins
def setup():
    # Setup board mode
    GPIO.setmode(GPIO.BOARD)
    # Setup regular GPIO
    for x in LED_value:
        GPIO.setup(x,GPIO.OUT)
        GPIO.output(x,0)

    GPIO.setup(btn_submit,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.setup(btn_increase,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    
    # Setup PWM channels
    GPIO.setup(LED_accuracy,GPIO.OUT)
    global led_pwm
    GPIO.setup(buzzer,GPIO.OUT)
    global buzzer_pwm
    led_pwm = GPIO.PWM(LED_accuracy,1000)
    buzzer_pwm = GPIO.PWM(buzzer,1)

    led_pwm.start(0)
    buzzer_pwm.start(0)
    # Setup debouncing and callbacks
    GPIO.add_event_detect(btn_increase,GPIO.RISING,callback=btn_increase_pressed,bouncetime=200)
    GPIO.add_event_detect(btn_submit,GPIO.FALLING,callback=btn_guess_pressed,bouncetime=200)

    currentGuess=0
    
    pass


# Load high scores
def fetch_scores():
    # get however many scores there are
    #sleep(0.01)
    #eeprom.populate_mock_scores()
    sleep(0.01)
    #block1 = eeprom.read_block(0,4)
    score_count=eeprom.read_byte(0)
    #score_count=block1[0]

    sleep(0.01)
    #tempCount = score_count
    # Get the scores
    counter=1
    scores=[]
    
    boolScore=True
    while boolScore==True:
        #print('test2')
        tempArr=eeprom.read_block(counter,4)
        
        if tempArr[0]!=0:
            name=''
            blockData=eeprom.read_block(counter,4)
            
            for i in range(0,3):
                if chr(blockData[i]).isalpha():
                    letter=chr(blockData[i])
                    name=name+letter
            tempScore = blockData[3]
            output=[name,tempScore]
            scores.append(output)
            counter+=1
            #score_count+=1
            #eeprom.write_byte(0,score_count)
            
        else:
            boolScore=False
    # convert the codes back to ascii
    # return back the results
    #print(score_count)
    #print(scores)
    return score_count, scores


# Save high scores
def save_scores():
    # fetch scores
    s_count, scores = fetch_scores()
    # include new score
    global playerName
    global playerScore
    print(playerName)
    tempName=playerName[:3]
    playerName[:3]
    #playerScore=3
    nameAndScore=[str(playerName),int(playerScore)]
    scores.append(nameAndScore)
    sleep(0.01)
    scores.sort(key=lambda x: x[1])
    for i, score in enumerate(scores):
        data_to_write = []
        a=0
        for letter in score[0]:
            #if letter<3:
            
            if a<3:
                data_to_write.append(ord(letter))
            else:
                break
            a+=1
        data_to_write.append(score[1])
        eeprom.write_block(i+1, data_to_write)
    score_count=eeprom.read_byte(0)
    #print(score_count)
    eeprom.write_byte(0,score_count+1)
    #print(eeprom.read_block(1,4))
    #print(eeprom.read_block(2,4))
    #print(eeprom.read_block(3,4))
    #print(eeprom.read_block(4,4))
    #print(eeprom.read_block(5,4))
    # sort
    # update total amount of scores
    # write new scores
    pass


# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)


# Increase button pressed
def btn_increase_pressed(channel):
    # Increase the value shown on the LEDs
    # You can choose to have a global variable store the user's current guess, 
    # or just pull the value off the LEDs when a user makes a guess
    #print('test1')
    #currentGuess=0
    global currentGuess
    currentGuess+=1
    if currentGuess==0:
        GPIO.output(LED_value[0],0)
        GPIO.output(LED_value[1],0)
        GPIO.output(LED_value[2],0)

    elif currentGuess==1:
        GPIO.output(LED_value[0],1)
        GPIO.output(LED_value[1],0)
        GPIO.output(LED_value[2],0)
     
    elif currentGuess==2:
        GPIO.output(LED_value[0],0)
        GPIO.output(LED_value[1],1)
        GPIO.output(LED_value[2],0)

    elif currentGuess==3:
        GPIO.output(LED_value[0],1)
        GPIO.output(LED_value[1],1)
        GPIO.output(LED_value[2],0)
    
    elif currentGuess==4:
        GPIO.output(LED_value[0],0)
        GPIO.output(LED_value[1],0)
        GPIO.output(LED_value[2],1)

    elif currentGuess==5:
        GPIO.output(LED_value[0],1)
        GPIO.output(LED_value[1],0)
        GPIO.output(LED_value[2],1)
     
    elif currentGuess==6:
        GPIO.output(LED_value[0],0)
        GPIO.output(LED_value[1],1)
        GPIO.output(LED_value[2],1)

    elif currentGuess==7:
        GPIO.output(LED_value[0],1)
        GPIO.output(LED_value[1],1)
        GPIO.output(LED_value[2],1)
    
    else:
        currentGuess=0
        GPIO.output(LED_value[0],0)
        GPIO.output(LED_value[1],0)
        GPIO.output(LED_value[2],0)
       
    pass


# Guess button
def btn_guess_pressed(channel):
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    # Change the PWM LED
    global playerScore
    start_time=time.time()
    while GPIO.input(channel)==0:
        pass
    buttonTime=time.time()-start_time
    if buttonTime>1:
        GPIO.output(LED_value[0],0)
        GPIO.output(LED_value[1],0)
        GPIO.output(LED_value[2],0)
        led_pwm.ChangeDutyCycle(0)
        buzzer_pwm.ChangeDutyCycle(0)
        led_pwm.stop()
        buzzer_pwm.stop()
        #currentGuess=0
        GPIO.cleanup()
        setup()
        menu()
    elif buttonTime>0.1:
        playerScore+=1
        #print('btn submit works')
        accuracy_leds()
        global playerName
    
    # if it's close enough, adjust the buzzer
    # if it's an exact guess:
    # - Disable LEDs and Buzzer
    # - tell the user and prompt them for a name 
    # - add the new score
    # - sort the scores
    # - Store the scores back to the EEPROM, being sure to update the score count
        if currentGuess==value:
            GPIO.output(LED_value[0],0)
            GPIO.output(LED_value[1],0)
            GPIO.output(LED_value[2],0)
            led_pwm.ChangeDutyCycle(0)
            buzzer_pwm.ChangeDutyCycle(0)
            led_pwm.stop()
            buzzer_pwm.stop()
            playerName = input("Congratulations, you won! Enter your name:\n")
            save_scores()
            GPIO.cleanup()
            setup()
            menu()
    else:
        pass    
    # if held clear and go to menu
    # Compare the actual value with the user value displayed on the LEDs
    
    pass


# LED Brightness
def accuracy_leds():
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    #print('accuracy_leds')
    global value
    if currentGuess<value:
        led_duty = currentGuess/value*100
        print(led_duty)
    elif currentGuess>value:
        led_duty = (8-currentGuess)/(8-value)*100
        print(led_duty)
    else:
        led_duty=100
        print(led_duty)
    led_pwm.ChangeDutyCycle(led_duty)
    
    pass

# Sound Buzzer
def trigger_buzzer():
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    #print('trigger_buzzer')
    temp = currentGuess-value
    #buzzer_pwm.start(50)
    if abs(temp)==1:
        buzzer_pwm.ChangeDutyCycle(50)
        buzzer_pwm.ChangeFrequency(4)
    elif abs(temp)==2:
        buzzer_pwm.ChangeDutyCycle(50)
        buzzer_pwm.ChangeFrequency(2)
    elif abs(temp)==3:
        buzzer_pwm.ChangeDutyCycle(50)
        buzzer_pwm.ChangeFrequency(1)
    else:
        buzzer_pwm.stop()
    pass


if __name__ == "__main__":
    try:
        # Call setup function
        setup()
        welcome()
        while True:
            menu()
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
