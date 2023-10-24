import RPi.GPIO as GPIO
import time 
import spidev
import random

import time
import board
import busio
import digitalio
from PIL import Image, ImageDraw , ImageFont
import adafruit_ssd1306
import subprocess
from flask import Flask, render_template, request
import requests 
from urllib.parse import urlencode, unquote
import json
import csv
import os

app = Flask(__name__)

GPIO.setwarnings(False)#불필요한 경고 제거 
GPIO.setmode(GPIO.BCM)

button_pin = 17 # button pin 설정
#button_pin1 =27
GPIO.setup(button_pin, GPIO.IN,pull_up_down=GPIO.PUD_DOWN) 
#GPIO.setup(button_pin1, GPIO.IN,pull_up_down=GPIO.PUD_DOWN) 
#oled 설정
oled_reset = digitalio.DigitalInOut(board.D4)

WIDTH = 128
HEIGHT =64 
BORDER = 5 

LOOPTIME = 1.0 
i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH,HEIGHT,i2c ,addr=0x3C,reset = oled_reset)

oled.fill(0)
oled.show()

image=Image.new("1",(oled.width,oled.height))
draw = ImageDraw.Draw(image)
draw.rectangle((0,0,oled.width,oled.height),outline=255,fill=255)

font = ImageFont.truetype('PixelOperator.ttf',24)


#spi 설정
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 100000
delay = 0.1

sw_channel = 0 
vrx_channel = 1 
vry_channel = 2



xZero =512
yZero =523

#LED_list = [14,15,18]
#핀설정
LED1 = 14 
LED2 = 15
LED3 = 18
buzzer = 4 
#GPIO.setup(LED_list,GPIO.OUT)
#출력설정
GPIO.setup(LED1,GPIO.OUT)
GPIO.setup(LED2,GPIO.OUT)
GPIO.setup(LED3,GPIO.OUT)
GPIO.setup(buzzer,GPIO.OUT)
#GPIO.output(LED_list,False)

#초기설정
GPIO.output(LED1,False)
GPIO.output(LED2,False)
GPIO.output(LED3,False)
p=GPIO.PWM(buzzer,1)

#버저 계음 설정
frq = []
#성공 실패 리스트 
list = []
#web 출력 숫자
truenum = 0
falsenum = 0
#game 실행 횟수
game_count = 0
#PWM 시작
p.start(50)

def Position(adcnum,zerovalue):
    return readadc(adcnum)-zerovalue

def readadc(adcnum):
    if adcnum>7 or adcnum<0:
        return -1
    r = spi.xfer2([1,(8+adcnum)<<4,0])
    data=((r[1]&3)<<8)+r[2]
    return data
def Countnum():
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    draw.text((30, 0),"1", font=font, fill=255)
    oled.image(image)
    oled.show()
    time.sleep(delay*20)
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    draw.text((30, 0),"2", font=font, fill=255)
    oled.image(image)
    oled.show()
    time.sleep(delay*20)
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    draw.text((30, 0),"3", font=font, fill=255)
    oled.image(image)
    oled.show()
    time.sleep(delay*20)  
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    draw.text((30, 0),"GO", font=font, fill=255)
    oled.image(image)
    oled.show()
    time.sleep(delay)

def LED(channel):
    
    if level == 1 :   
        frq = Selectlevel(level) 
        Countnum()
        PlayGame(frq)
    if level == 2 :   
        frq = Selectlevel(level) 
        Countnum()
        PlayGame(frq)
    if level == 3 :   
        frq = Selectlevel(level) 
        Countnum()
        PlayGame(frq)

def Selectlevel(level):
 
    if level == 1:
        return [330,349,330,294,262,494,349,294,262,493,330]
    elif level == 2:
        return [330,349,330,294,262,494,349,294,262,493,330,330,349,330,294,262,494,349,294,262,493,330]
    else:
        return [330,349,330,294,262,494,349,294,262,493,330,330,349,330,294,262,494,349,294,262,493,330,330,349,330,294,262,494,349,294,262,493,330]

def PlayGame(frq):
    score_list = []
    for fr in frq:
        time.sleep(delay)
        p.ChangeFrequency(fr) #frq 수 만큼 fr을 반복하여 음 변경
        if level == 1:
            gamedelay = delay* 8
        elif level == 2:
            gamedelay = delay* 4
        elif level == 3:
            gamedelay = delay* 2
        if fr%3 == 0:
            GPIO.output(LED1,True)
            time.sleep(gamedelay)
            if vry_val<-400:
                score_list.append(True)
                draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
                draw.text((20, 30),"NICE", font=font, fill=255)
                oled.image(image)
                oled.show()
            else:
                score_list.append(False)
                draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
                draw.text((20, 30),"BAD", font=font, fill=255)
                oled.image(image)
                oled.show()
        elif fr%3 == 1:
            GPIO.output(LED2,True)
            time.sleep(gamedelay)
            if abs(vrx_val)<40 and abs(vry_val)<40:
                score_list.append(True)
                draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
                draw.text((20, 30),"NICE", font=font, fill=255)
                oled.image(image)
                oled.show()
            else:
                score_list.append(False)
                draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
                draw.text((20, 30),"BAD", font=font, fill=255)
                oled.image(image)
                oled.show()
        elif fr%3 == 2:
            GPIO.output(LED3,True)
            time.sleep(gamedelay)
            if vry_val>400:
                score_list.append(True)
                draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
                draw.text((20, 30),"NICE", font=font, fill=255)
                oled.image(image)
                oled.show()
            else:
                score_list.append(False)
                draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
                draw.text((20, 30),"BAD", font=font, fill=255)
                oled.image(image)
                oled.show()
        print(score_list)
        
        time.sleep(delay)
        
        GPIO.output(LED1,False)
        GPIO.output(LED2,False)            
        GPIO.output(LED3,False)
    list = score_list
    GPIO.cleanup()
    OutScore(list)
   
GPIO.add_event_detect(button_pin,GPIO.RISING,callback=LED,bouncetime = 300)

def OutScore(list):
    num1 = 0
    num2 = 0
    for i in list:
        if i == True:
            num1 += 1
        else:
            num2 += 1
    truenum = num1
    falsenum = num2
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    draw.text((0, 0),"NICE", font=font, fill=255)
    draw.text((0, 30),"%d" %num1, font=font, fill=255)
    draw.text((50, 0),"BAD", font=font, fill=255)
    draw.text((50, 30),"%d" %num2, font=font, fill=255)
    oled.image(image)
    oled.show()
    
    
    persent =(truenum/(truenum+falsenum))*100
    
    rate = ""
    
    if persent == 100:
        rate = "Perfect"
    elif persent >=75 and persent<100:
        rate = "Best"
    elif persent >=50 and persent<75:
        rate = "Good"
    else:
        rate = "Bad"
    
    @app.route("/")
    def index():
        return render_template(
            "index.html",
            webtruenum=truenum,
            webfalsenum=falsenum,
            webrate=rate,
            webpersent ="%d" %persent,
        )
        
    if __name__ == "__main__":
        app.run(host='0.0.0.0')
    
level = 0 
try:
    
    while 1:
        draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
        #time.sleep(delay)
        draw.text((0, 0),"SELECT-LEVEL", font=font, fill=255)
    
        sw_val = readadc(sw_channel)
        vrx_val = Position(vrx_channel,xZero)
        vry_val = Position(vry_channel,yZero)
        if level == 0 :
            if vry_val<-400:
                draw.text((0, 30),"EASY", font=font, fill=255)
            elif abs(vrx_val)<40 and abs(vry_val)<40:
                draw.text((0, 30),"NORMAL", font=font, fill=255)
            elif vry_val>400:
                draw.text((0, 30),"HARD", font=font, fill=255)
            oled.image(image)
            oled.show()
        
            if GPIO.event_detected(button_pin) and level == 0:
                if vry_val<-400:
                    level = 1
                    GPIO.output(LED1,True)
                    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
                    draw.text((30, 0),"SELECT", font=font, fill=255)
                    draw.text((30, 30),"EASY", font=font, fill=255)
                    oled.image(image)
                    oled.show()
                    time.sleep(0.5)
                    GPIO.output(LED1,False)
                elif abs(vrx_val)<40 and abs(vry_val)<40:
                    level = 2
                    GPIO.output(LED2,True)
                    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
                    draw.text((30, 0),"SELECT", font=font, fill=255)
                    draw.text((30, 30),"NORMAL", font=font, fill=255)
                    oled.image(image)
                    oled.show()
                    time.sleep(0.5)
                    GPIO.output(LED2,False)
                elif vry_val>400:                
                    level = 3
                    GPIO.output(LED3,True)
                    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
                    draw.text((30, 0),"SELECT", font=font, fill=255)
                    draw.text((30, 30),"HARD", font=font, fill=255)
                    oled.image(image)
                    oled.show()
                    time.sleep(0.5)
                    GPIO.output(LED3,False)
        
        # GPIO.output(LED1,False)
        # GPIO.output(LED2,False)            
        # GPIO.output(LED3,False)
        
        time.sleep(delay)
        
except KeyboardInterrupt:
    pass

oled.poweroff()
#pwm 정지
p.stop() 
#GPIO 설정 없앰
GPIO.cleanup()

