import serial
import time

from RPi import GPIO
from Settings import const_distaces

#tipo di riferimento, numerazione della cpu
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN)

#Lasers
L_front_L = 0
L_front_R = 1
L_right_L = 2
L_right_R = 3
L_back_R = 4
L_back_L = 5
L_left_L = 6
L_left_R = 7


# /dev/ttyACM0 is STM32F103C8
# /dev/ttyUSB0 is Arduino Nano

def isLack():
    if GPIO.input(23):
        return True
    else:
        return False

def isWall(millisL, millisR):
    if (millisR + millisL) < (const_distaces.WALL_MAX * 2):
        return True
    else:
        return False


def getNano():
    serNano.write("0\n".encode('utf-8'))
    while serNano.in_waiting == 0:
        time.sleep(0.001)
    line = float((serNano.readline().decode('utf-8').rstrip()))
    return line


def robotSinistra():
    angle = getNano()
    finish = angle - 90
    if angle < -90:
        finish = 0
    serSTM.write("13\n".encode('utf-8'))
    while angle > finish:
        angle = getNano()
        print(angle)
    serNano.write("1\n".encode('utf-8'))
    if isWall(lasers[L_right_L], lasers[L_right_R]):
        serSTM.write("15\n".encode('utf-8'))


def robotDestra():
    angle = getNano()
    finish = angle + 90
    if angle > 90:
        finish = 0
    serSTM.write("12\n".encode('utf-8'))
    while angle < finish:
        angle = getNano()
        print(angle)
    serNano.write("1\n".encode('utf-8'))
    if isWall(lasers[L_right_L], lasers[L_right_R]):
        serSTM.write("15\n".encode('utf-8'))


def getLasers():
    serSTM.write("3\n".encode('utf-8'))
    print("get lasers")
    lasers = []
    for i in range(8):
        while serSTM.in_waiting == 0:
            time.sleep(0.001)
        line = float((serSTM.readline().decode('utf-8').rstrip()))
        print("laser = " + str(line))
        lasers.append(line)
    return lasers


def robotAvanti():
    serSTM.write("10\n".encode('utf-8'))


def robotIndietro():
    serSTM.write("12\n".encode('utf-8'))
    serSTM.write("15\n".encode('utf-8'))
    serSTM.write("12\n".encode('utf-8'))
    serSTM.write("15\n".encode('utf-8'))
    serSTM.write("10\n".encode('utf-8'))


if __name__ == '__main__':
    reset = False
    serSTM = serial.Serial('/dev/ttyACM0', 115200, timeout=2)  # ACM0 == STM32F103C8
    serSTM.reset_input_buffer()
    serNano = serial.Serial('/dev/ttyUSB0', 57600, timeout=1)  # USB0 == Arduino Nano
    serNano.reset_input_buffer()
    while True:
        while not isLack():
            lasers = getLasers()
            if not isWall(lasers[L_right_L], lasers[L_right_R]):
                print("DESTRA")
                robotDestra()
                robotAvanti()
            elif not isWall(lasers[L_front_L], lasers[L_front_R]):
                print("AVANTI")
                robotAvanti()
            elif not isWall(lasers[L_left_L], lasers[L_left_R]):
                print("SINISTRA")
                robotSinistra()
                robotAvanti()
            elif not isWall(lasers[L_back_L], lasers[L_back_R]):
                print("INDIETRO")
                robotIndietro()
            while serSTM.in_waiting == 0:
                time.sleep(0.001)
            line = (serSTM.readline().decode('utf-8').rstrip())
            print(line)
            if line == "0":
                robotIndietro()
            if line == "11":
                time.sleep(5)
        while isLack():
            serSTM.setDTR(False)
            time.sleep(0.5)
            serSTM.setDTR(True)
            serSTM.setRTS(False)
            serSTM.setRTS(True)

            serNano.setDTR(False)
            time.sleep(0.5)
            serNano.setDTR(True)
            serNano.setRTS(False)
            serNano.setRTS(True)
