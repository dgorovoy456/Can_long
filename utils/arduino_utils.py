import time


def arduino_enable_blue(arduino_serial):
    time.sleep(3)
    arduino_serial.write(b'1')
    time.sleep(2)


def arduino_enable_red(arduino_serial):
    time.sleep(3)
    arduino_serial.write(b'2')
    time.sleep(2)
