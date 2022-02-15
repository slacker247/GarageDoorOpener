import serial
import numpy as np
import time
import gpiozero

relay = gpiozero.DigitalOutputDevice(pin=17)

def read_tfluna_data():
    distance = 0.0
    strength = 0.0
    temperature = 0.0
    try:
        ser = serial.Serial("/dev/ttyS0", 115200,timeout=0) # mini UART serial device
        if ser.isOpen() == False:
            ser.open() # open serial port if not open
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
                    break
        ser.close() # close serial port
    except:
        time.sleep(3)
    return distance/100.0,strength,temperature

distance,strength,temperature = read_tfluna_data() # read values
print('Distance: {0:2.2f} m, Strength: {1:2.0f} / 65535 (16-bit), Chip Temperature: {2:2.1f} C'.\
        format(distance,strength,temperature)) # print sample data
lastDist = distance
err_margin = 0 # 0.06
d_margin = 0.06
delta = 0
lastState = 0
state = 0 # 0 unk, 1 closed, 2 opening, 3 open, 4 closing
while True:
    lastState = state
    distance,strength,temperature = read_tfluna_data() # read values
    if distance > 0:
        delta += abs(distance - lastDist)
        if delta > err_margin:
            err_margin = delta
        if delta > d_margin:
            # print only if it's changed
            print(f"Distance: {distance:2.2f} m")
            #print('Distance: {0:2.2f} m, Strength: {1:2.0f} / 65535 (16-bit), Chip Temperature: {2:2.1f} C'.\
            #        format(distance,strength,temperature)) # print sample data
            #print(f"Margin of error: {err_margin}")
        if delta < d_margin and state == 2:
            # cycle open
            print("Cycle open")
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
        if distance > (2.54 - d_margin):
            state = 1
            if not lastState == state:
                print("State: closed")
            lastDist = distance
            delta = 0
        if lastDist - distance > d_margin:
            state = 2
            print("State: opening")
            lastDist = distance
            delta = 0
        if distance - lastDist > d_margin:
            state = 4
            print("State: closing")
            lastDist = distance
            delta = 0
        if distance < (0.45 + d_margin):
            state = 3
            if not lastState == state:
                print("State: open")
            lastDist = distance
            delta = 0
        if not state == lastState:
            err_margin = 0
    time.sleep(0.5)
    pass

