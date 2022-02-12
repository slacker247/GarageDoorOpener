import serial,time
import numpy as np
import time
import gpiozero

ser = serial.Serial("/dev/ttyS0", 115200,timeout=0) # mini UART serial device
relay = gpiozero.DigitalOutputDevice(pin=17)

def read_tfluna_data():
    while True:
        counter = ser.in_waiting # count the number of bytes of the serial port
        if counter > 8:
            bytes_serial = ser.read(9) # read 9 bytes
            ser.reset_input_buffer() # reset buffer

            if bytes_serial[0] == 0x59 and bytes_serial[1] == 0x59: # check first two bytes
                distance = bytes_serial[2] + bytes_serial[3]*256 # distance in next two bytes
                strength = bytes_serial[4] + bytes_serial[5]*256 # signal strength in next two bytes
                temperature = bytes_serial[6] + bytes_serial[7]*256 # temp in next two bytes
                temperature = (temperature/8.0) - 256.0 # temp scaling and offset
                return distance/100.0,strength,temperature

if ser.isOpen() == False:
    ser.open() # open serial port if not open

lastDist = 0.0
state = 0 # 0 unk, 1 closed, 2 opening, 3 open, 4 closing
while ser.isOpen():
    distance,strength,temperature = read_tfluna_data() # read values
    if distance - lastDist == 0 and state == 2:
        # cycle open
        # close door
        relay.on()
        time.sleep(0.14)
        relay.off()
        # stop close
        time.sleep(1)
        relay.on()
        time.sleep(0.14)
        relay.off()
        # open door
        time.sleep(1)
        relay.on()
        time.sleep(0.14)
        relay.off()
        pass
    if distance > 2 and distance < 3:
        state = 1
        print("State: closed")
        lastDist = distance
    if lastDist - distance > 0:
        state = 2
        print("State: opening")
        lastDist = distance
    if distance - lastDist > 0:
        state = 4
        print("State: closing")
        lastDist = distance
    if distance > 0 and distance < 0.6:
        state = 3
        print("State: open")
        lastDist = distance
    print('Distance: {0:2.2f} m, Strength: {1:2.0f} / 65535 (16-bit), Chip Temperature: {2:2.1f} C'.\
                format(distance,strength,temperature)) # print sample data
    time.sleep(5)
    pass

ser.close() # close serial port
