import smtplib  # library for sending email from Rpi
import RPi.GPIO as GPIO  # import the GPIO library for connecting sensors
import time  # library to use timestamp function
from email.mime.multipart import MIMEMultipart  # func. Under smtp lib
from email.mime.text import MIMEText
from urllib.request import urlopen  # libfunc to start ThingSpeak Connection
from gpiozero import MotionSensor
import sys
# import urllib2
from time import sleep
import datetime
import Adafruit_DHT as dht  # library for interfacing adafruit sensors

fromaddr = "ece442iit@gmail.com"
toaddr = "" # TODO: Add email addresses separated by commas
alladdr = toaddr.split(",")


GPIO.setmode(GPIO.BCM)
GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_UP)
pir = MotionSensor(7)  # connects the gpio pin7 to PIR sensor
# Enter Your API key here
myAPI = 'TEBE1PSLZEXL6BED'
# URL where we will send the data
baseURL = 'https://api.thingspeak.com/update?api_key=%s' % myAPI
count_det = 0
count_temp = 0
pin = 4  # connects gpio pin4 to DHT22
flag = 0
file = open("Data_Log.txt", "a+")  # creating a text file to store sensor op
now = datetime.datetime.now()


def DHT22_data():
    # Reading from DHT22 and storing the temperature and humidity
    humi, temp = dht.read_retry(dht.DHT22, pin)  # read temp & humi data
    return humi, temp


try:
    while True:
        humi, temp = DHT22_data()
        # display temp and humi on terminal
        print('Temp: {0:0.1f}*C  Humidity: {1:0.1f}%'.format(temp, humi))

        if isinstance(humi, float) and isinstance(temp, float):
            # check if motion is detected in PIR
            if pir.motion_detected:
                flag = 1
                print('Motion Detected')
                file.write(now.strftime("%m/%d/%Y, %H:%M:%S"))
                file.write(" Motion Detected!\n")
                count_det = count_det + 1  # if detected increase counter
            else:
                flag = 0
                print('Motion Not Detected')

            if count_det == 3:  # if count reaches 3 initiate email trigger
                msg = MIMEMultipart()
                msg['From'] = fromaddr
                msg['To'] = toaddr
                msg['Subject'] = "Test Alert"
                body = 'Intruder detected, please open live stream at URL: http://192.168.137.162:8081/0/'
                msg.attach(MIMEText(body, 'plain'))
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.ehlo
                server.starttls()
                server.login(fromaddr, "iot@ece442")
                text = msg.as_string()
                server.sendmail(fromaddr, alladdr, text)
                server.quit()
                count_det = count_det + 1  # Increases counter so that mail is not repeatedly sent

        humi = '%.2f' % humi
        temp = '%.2f' % temp
        # print (temp, humi)
        file.write(now.strftime("%m/%d/%Y, %H:%M:%S"))
        file.write('Temp: {}*C  Humidity: {}%\n'.format(temp, humi))

        if temp >= "40.00":  # check temperature cond if >40 inc. count
            count_temp = count_temp + 1
            if count_temp == 2:  # if count equals 2 then trigger email
                msg = MIMEMultipart()
                msg['From'] = fromaddr
                msg['To'] = toaddr
                msg['Subject'] = "Test Alert"
                body = 'Fire detected, please open live stream at URL: http://192.168.137.162:8081/0/'
                msg.attach(MIMEText(body, 'plain'))
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.ehlo
                server.starttls()
                server.login(fromaddr, "iot@ece442")
                text = msg.as_string()
                server.sendmail(fromaddr, alladdr, text)
                server.quit()
            # Sending the data to thingspeak
                conn = urlopen(baseURL + '&field1=%s&field2=%s&field3=%s' % (temp, humi, flag))
                print(conn.read())
                # Closing the connection
                conn.close()

        else:
            print('Error')
            # DHT22 requires 2 seconds to give a reading, so make sure to add delay of above 2 seconds.
            sleep(5)
except KeyboardInterrupt:  # press any key on keyboard to stop terminal prg
    pass
file.close()
