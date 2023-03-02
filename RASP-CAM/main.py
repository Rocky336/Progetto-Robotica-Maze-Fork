import serial
import time
import math

from mpu6050 import mpu6050
from camera import Camera
from analysis import read_all

from Settings import const_distaces

# Initialize MPU6050 sensor
sensor = mpu6050(0x68)
# Define constant for MPU6050
RAD_TO_DEG = 57.295779513082320876798154814105

L_frontUp = 0
L_frontDown = 1
L_right = 2
L_left = 3
L_back = 4

busses = Camera.list_cameras()
r_camera = Camera('/dev/video0')
#r_camera = Camera('/dev/video2')

def get_pitch():
    accel_data = sensor.get_accel_data()
    x = accel_data['x']
    y = accel_data['y']
    z = accel_data['z']
    pitch = math.atan2(-x, math.sqrt(y*y + z*z))
    pitch_deg = pitch * RAD_TO_DEG
    if pitch_deg > 180:
        pitch_deg = pitch_deg - 360
    return pitch_deg

def isWall(millis):
    if  millis < const_distaces.WALL_MAX:
        return True
    else:
        return False

#def read_wallsL():
#    time.sleep(1.5)
#    out = 0
#    letter, color = read_all(l_camera)
#    print(f'L: letter({letter}) color({color})')
#    out += {'': 0, 'g': 1, 'y': 2, 'r': 2}[color]
#    if out == 0:
#        out += {'': 0, 'u': 0, 's': 0, 'h': 0}[letter]
#    if out > 0:
#        return out << 4

def read_wallR():
    time.sleep(1.5)
    out = 0
    letter, color = read_all(r_camera)
    print(f'R: letter({letter}) color({color})')
    out += {'': 0, 'g': 1, 'y': 2, 'r': 2}[color]
    if out == 0:
        out += {'': 0, 'u': 1, 's': 3, 'h': 4}[letter]
    print("numero mattoni")
    print(out)
    cagaMattoni(out)
    
def robotSx():
    lasers = getLasers()
    ser.write("13\n".encode('utf-8'))
    if isWall(lasers[L_right]):
        print('Back adjust')
        ser.write("15\n".encode('utf-8'))
    elif isWall(lasers[L_left]):        
        print('Front adjust')
        ser.write("16\n".encode('utf-8'))

def robotDx():
    lasers = getLasers()
    ser.write("12\n".encode('utf-8'))
    if isWall(lasers[L_left]):
        print('Back adjust')
        ser.write("15\n".encode('utf-8'))
    elif isWall(lasers[L_right]):
        print('Front adjust')
        ser.write("16\n".encode('utf-8'))

def getLasers():
    ser.write("3\n".encode('utf-8'))
    print("get lasers")
    lasers = []
    for i in range(5):
        while ser.in_waiting == 0:
            time.sleep(0.001)
        line = float((ser.readline().decode('utf-8').rstrip()))
        print("laser = " + str(line))
        lasers.append(line)
    return lasers

def ctrlCam():
    ls = getLasers()
    rotation = 0
    if isWall(ls[L_right]):
        read_wallR()
    if isWall(ls[L_frontUp]):
        rotation = -1
        robotSx()
        read_wallR()
    if rotation == -1:
        if isWall(ls[L_left]):
            robotSx()
            read_wallR()
            rotation = -2
        if isWall(ls[L_back]):
            if rotation == -2:
                robotSx()
                read_wallR()
                robotSx()
                rotation = 0
            else:
                robotSx()
                robotSx()
                read_wallR()
                robotSx()
                rotation = 0
    else:
        if isWall(ls[L_back]):
            robotDx()
            read_wallR()
            rotation = 1
        if isWall(ls[L_left]):
            if rotation == 1:
                robotDx()
                read_wallR()
                rotation = 2
            else:
                robotDx()
                robotDx()
                read_wallR()
                rotation = 2
    if rotation > 0:
        for i in range(rotation):
            robotSx()
    else:
        for i in range((-rotation)):
            robotDx()

def blinkVictim():
    ser.write("0\n".encode('utf-8'))

def cagaMattoni(n):
    print("N mattoni + 1 :")
    print(n)
    if n > 0:
        blinkVictim()
    for i in range(n-1):
        ser.write("2\n".encode('utf-8'))

def robotBack():
    ser.write("12\n".encode('utf-8'))
    ser.write("15\n".encode('utf-8'))
    ser.write("12\n".encode('utf-8'))
    ser.write("15\n".encode('utf-8'))

def robotForward():
    ser.write("10\n".encode('utf-8'))

def forwardCase():
    ls = getLasers()
    up = ls[L_frontUp]
    down = ls[L_frontDown]
    if (up - down) > const_distaces.DELTA_FRONT and (up > const_distaces.MIN_FRONT_UP and down > const_distaces.MIN_FRONT_DOWN):
        c = True
        print("RAMPA")
        ser.write("14\n".encode('utf-8'))
        time.sleep(const_distaces.TIME_BEFORE_RAMPA)
        pitch = get_pitch()
        while c:
            if pitch > -const_distaces.DELTA_PENDENZA and  pitch < const_distaces.DELTA_PENDENZA:
                ser.write("ZIO PERA\n".encode('utf-8'))
                c = False
    else:
        print()
        robotForward()

if __name__ == '__main__':
    time.sleep(5)
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=5)
    ser.reset_input_buffer()
    condition = True
    while condition:
        print("-----CAM MOVEMENTS-----")
        ctrlCam()
        print("-----RUN MOVEMENTS-----")
        lasers = getLasers()
        if not isWall(lasers[L_right]):
            print("DESTRA")
            robotDx()
            forwardCase()
        elif not isWall(lasers[L_frontUp]):
            print("AVANTI")
            forwardCase()
        elif not isWall(lasers[L_left]):
            print("SINISTRA")
            robotSx()
            forwardCase()
        elif not isWall(lasers[L_back]):
            print("INDIETRO")
            robotBack()
            forwardCase()
        while ser.in_waiting == 0:
            time.sleep(0.001)
        line = (ser.readline().decode('utf-8').rstrip())
        print(line)
        if line == "0":
            robotBack()
        if line == "11":
            time.sleep(5)
