import serial
import time

from Settings import const_distaces

# L_frontUp = 0
# L_frontDown = 1
# L_right = 2
# L_left = 3
# L_back = 4

L_front_R = 0
L_front_L = 1
L_left_R = 2
L_left_L = 3
L_back_L = 4
L_back_R = 5
L_right_R = 6

laserName = ["L_front_R", "L_front_L", "L_left_L", "L_back_L", "L_back_R", "L_right_R"]

# /dev/ttyACM0 is STM32F103C8
# /dev/ttyUSB0 is Arduino Nano

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
    print("GIRAMENTO A SINISTRA")
    angle = getNano()
    finish = angle - 90
    if angle < -90:
        finish = 0
    lasers = getLasers()
    serSTM.write("13\n".encode('utf-8'))
    while angle > finish:
        angle = getNano()
        print(angle)
    serNano.write("1\n".encode('utf-8'))
    if isWall(lasers[L_right_R], lasers[L_right_R]):
        print("Back adjust")
        serSTM.write("15\n".encode('utf-8'))
    elif isWall(lasers[L_left_L], lasers[L_left_L]):
        print("Front adjust")
        serSTM.write(("16\n".encode('utf-8')))


def robotDestra():
    print("GIRAMENTO A DESTRA")
    angle = getNano()
    finish = angle + 90
    if angle > 90:
        finish = 0
    lasers = getLasers()
    serSTM.write("12\n".encode('utf-8'))
    while angle < finish:
        angle = getNano()
        print(angle)
    serNano.write("1\n".encode('utf-8'))
    if isWall(lasers[L_right_R], lasers[L_right_R]):
        print("Back adjust")
        serSTM.write("15\n".encode('utf-8'))
    elif isWall(lasers[L_left_L], lasers[L_left_L]):
        print("Front adjust")
        serSTM.write(("16\n".encode('utf-8')))


def getLasers():
    serSTM.write("3\n".encode('utf-8'))
    print("get lasers")
    lasers = []
    for i in range(6):
        while serSTM.in_waiting == 0:
            time.sleep(0.002)
        line = float((serSTM.readline().decode('utf-8').rstrip()))
        print(laserName[i] + ": " + str(line))
        lasers.append(line)
    return lasers


def robotAvanti():
    serSTM.write("10\n".encode('utf-8'))


def robotIndietro():
    robotDestra()
    robotDestra()


if __name__ == '__main__':
    condition = False
    while not condition:
        try:
            print("Serial STM")
            serSTM = serial.Serial('/dev/ttyACM0', 115200, timeout=2)  # ACM0 == STM32F103C8
            serSTM.reset_input_buffer()
            print("Serial Nano")
            serNano = serial.Serial('/dev/ttyUSB0', 57600, timeout=1)  # USB0 == Arduino Nano
            serNano.reset_input_buffer()
            condition = True
        except:
            print("Serial waiting")
    while condition:
        lasers = getLasers()
        if not isWall(lasers[L_right_R], lasers[L_right_R]):
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
            time.sleep(0.002)
        line = (serSTM.readline().decode('utf-8').rstrip())
        print(line)
        if line == "0":
            robotIndietro()
        if line == "11":
            time.sleep(5)
