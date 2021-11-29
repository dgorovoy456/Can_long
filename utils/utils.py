import os
import time
import multiprocessing
import subprocess
from utils.wait import wait
from utils import failed_counter

import serial


def read_from_port(ser,
                   file_name
                   ):
    file = open(file_name, "ab")
    with ser, file:
        try:
            while True:
                line = ser.readline()
                if b'BL2: Booting BL31' in line:
                    print('Fuck')
                file.write(line)
                file.flush()
        except Exception as e:
            print(e)
    file.close()


def read_from_logcat(device_serial: str, file_name):
    p = subprocess.Popen(f'adb -s {device_serial} logcat'.split(), stdout=subprocess.PIPE, bufsize=1)
    with open(file_name, "a") as file:
        for line in p.stdout:
            file.write(line.decode('utf-8'))
            file.flush()


def thread_read(target, ser, file_name):
    proc = multiprocessing.Process(target=target, args=(ser, file_name))
    proc.start()
    return proc


def exception_group_checker(usb: str, log_dir: str, end_time: int, current_exception, iteration: int, log_file):
    LOG_DIR = log_dir
    print(f'End time :[{end_time}]')
    if current_exception is not None:
        print(f'Reboot [{iteration}] failed with reason [{current_exception}]')
        file_name = f'{LOG_DIR}/{iteration}_minicom_{current_exception}'
        if not log_contains_android_domain(log_file=log_file):
            file_name = f'{file_name}_miss_domain.log'
            os.rename(log_file,
                      file_name)
        else:
            os.rename(log_file,
                      f'{file_name}.log')
        try:
            ser = serial.Serial(usb, 115200)
            if not ser.isOpen():
                ser.open()
                wait(condition=lambda: ser.isOpen(),
                     max_timeout=30)
            xen_log = f'{LOG_DIR}/{iteration}_journalctl_{current_exception}.log'
            xen_stored_log(ser, xen_log)
            if log_contains_cr7_error(xen_log):
                failed_counter.cr7_failed += 1
                os.rename(xen_log,
                          f'{LOG_DIR}/{iteration}_journalctl_{current_exception}_CR7_ERROR.log')
        except:
            pass
    else:
        print(f'Reboot [{iteration}] success')
        try:
            ser = serial.Serial(usb, 115200)
            if not ser.isOpen():
                ser.open()
                wait(condition=lambda: ser.isOpen(),
                     max_timeout=30)
            xen_log = f'{LOG_DIR}/{iteration}_journalctl.log'
            xen_stored_log(ser, xen_log)
        except:
            pass


def xen_stored_log(ser, file_name):
    ser.flushInput()
    ser.flushOutput()
    time.sleep(3)
    ser.write(b'journalctl -fe\r\n')
    proc = thread_read(read_from_port, ser, file_name)
    time.sleep(30)
    proc.terminate()
    proc.join()
    if ser.isOpen():
        ser.close()
        time.sleep(2)


def log_contains_android_domain(log_file) -> bool:
    result = False
    with open(log_file, 'rb') as f:
        for line in f.readlines():
            if b'Android-9' in line:
                result = True
                break
    return result


def log_contains_cr7_error(log_file) -> bool:
    result = False
    with open(log_file, 'rb') as f:
        for line in f.readlines():
            if b"E: CR7::Flasher: Can't connect to cr7" in line:
                result = True
                break
    return result
