import keyboard
import serial

duino = serial.Serial('COM4', 115200, timeout=1)

def sendToSerial(data):
	duino.write(data.encode())

while True:
    if(keyboard.is_pressed('w')):
        sendToSerial("upsmally")
    elif keyboard.is_pressed('s'):
        sendToSerial("downsmally")
