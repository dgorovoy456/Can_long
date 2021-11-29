import os
import time


def shutdown_device(phi_n):
    command_shutdown = f'phidutil2 -p {phi_n} 1'
    os.system(command=command_shutdown)


def turn_on_device(phin_n):
    command_turn_on = f'phidutil2 -p {phin_n} 0'
    os.system(command=command_turn_on)


def reboot_device(phi_n):
    shutdown_device(phi_n)
    time.sleep(3)
    turn_on_device(phi_n)
    time.sleep(3)
