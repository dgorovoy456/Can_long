import os
import shutil
import time
import yagmail
import pytest
import subprocess
import serial

from utils.port_reader import PortReader
from utils import failed_counter
from utils.loggers import Logger, FixtureLogger

LOG_DIR = 'logs'
ENABLE_CAMERA_LOG_FILE = '/resources/rcv_cam_on.log'


@pytest.fixture(scope='function', autouse=False)
def init_fixture(request):
    DEVICE = os.getenv("DEVICE").strip()
    # DEVICE = '0000'
    USB = f'/dev/{os.getenv("USB")}'
    # USB = '/dev/ttyUSB0'
    USB_CR7 = f'{os.getenv("USB_CR7")}'
    # USB_CR7 = 'None'
    VideoInput = os.getenv('VideoInput')
    # VideoInput = '/dev/video2'
    TESTING_TIME = int(os.getenv('TESTING_TIME'))
    # TESTING_TIME = '2'
    REBOOT_COUNT = int(os.getenv('REBOOT_COUNT'))
    # REBOOT_COUNT = '2'
    ARDUINO_SERIAL = f'/dev/{os.getenv("ARDUINO_SERIAL")}'
    # ARDUINO_SERIAL = '/dev/ttyACM0'
    PHIDGET_PORT = os.getenv('PHIDGET_PORT')
    # PHIDGET_PORT = '0'
    PCan = os.getenv('PCan')
    # PCan = 'true'
    node = os.getenv("node")

    testDirName = f'{LOG_DIR}/{request.node.name}'
    camera_capture_dir = f'{testDirName}/capture_images'
    camera_diff_dir = f'{testDirName}/diff_images'

    if os.path.exists(path=testDirName):
        shutil.rmtree(testDirName)
    os.makedirs(testDirName)
    if os.path.exists(path=camera_capture_dir):
        shutil.rmtree(camera_capture_dir)
    os.makedirs(camera_capture_dir)
    if os.path.exists(path=camera_diff_dir):
        shutil.rmtree(camera_diff_dir)
    os.makedirs(camera_diff_dir)

    request.cls.DEVICE = DEVICE
    request.cls.LOG_DIR = LOG_DIR
    request.cls.VideoInput = VideoInput
    request.cls.TESTING_TIME = TESTING_TIME
    request.cls.REBOOT_COUNT = REBOOT_COUNT
    request.cls.USB = USB
    request.cls.USB_CR7 = USB_CR7
    request.cls.ARDUINO_SERIAL = ARDUINO_SERIAL
    request.cls.PHIDGET_PORT = PHIDGET_PORT
    request.cls.node = node
    request.cls.PCan = PCan
    request.cls.testDirName = testDirName
    request.cls.camera_capture_dir = camera_capture_dir
    request.cls.camera_diff_dir = camera_diff_dir

    MODEL = ''
    BUILD_ID = ''

    try:
        BUILD_ID = subprocess.check_output(
            f'adb -s {DEVICE.strip()} shell getprop ro.build.version.incremental'.split(),
            timeout=30).decode().strip()
    except Exception as e:
        print(f'Build id not found {e}')

    try:
        MODEL = subprocess.check_output(
            f'adb -s {DEVICE.strip()} shell getprop ro.product.model'.split(),
            timeout=30).decode().strip()
    except Exception as e:
        print(f'ADB device not found {e}')

    yield [DEVICE, ARDUINO_SERIAL, PHIDGET_PORT, node, USB_CR7, USB, PCan, testDirName]
    if request.node.name == 'test_camera_reboot':
        global_failed = failed_counter.adb_failed + \
                        failed_counter.boot_complete_failed + \
                        failed_counter.screen_on_failed + \
                        failed_counter.unknown_failed

        ration = (((int(TESTING_TIME) - global_failed) / int(TESTING_TIME)) * 100)
        print(f'Success ratio: [{ration}]')
        print(f'Successful boot attempts: [{(int(TESTING_TIME) - global_failed)}]')
        print(f'Failed boot attempts: [{global_failed}]')
        print(f' - Failed on adb device boot: [{failed_counter.adb_failed}]')
        print(f' - Failed on boot complete: [{failed_counter.boot_complete_failed}]')
        print(f' - Failed on screen on: [{failed_counter.screen_on_failed}]')
        print(f' - Failed on activity manager: [{failed_counter.activity_manager_failed}]')
        print(f' - Failed on camera is enable: [{failed_counter.camera_failed}]')
        print(f' - Unknown exceptions: [{failed_counter.unknown_failed}]')

        print('    ---------------- Failed subcategory ------------------')
        print(f'     - CR7 error: [{failed_counter.cr7_failed}]')
        print(f'Average boot time: [{int(failed_counter.average_boot_time / int(TESTING_TIME))}]')

        os.environ["DEBUSSY"] = "1"

        JOBURL = os.getenv('BUILD_URL')
        MESSAGE = f'Node: [{node}]\n' \
                  f'Serial: [{DEVICE}]\n' \
                  f'Model: [{MODEL}]\n' \
                  f'Build id: [{BUILD_ID}]\n' \
                  f'USB: [{USB}]\n' \
                  f'Phidget serial: [{PHIDGET_PORT}]\n' \
                  f'Phidget port: [{PHIDGET_PORT}]\n' \
                  f'Reboot count: [{TESTING_TIME}]\n' \
                  f'    ---------------- Statistic ------------------\n' \
                  f'Success ratio: [{ration}]\n' \
                  f'Successful boot attempts: [{(int(TESTING_TIME) - global_failed)}]\n' \
                  f'Failed boot attempts: [{global_failed}]\n' \
                  f' - Failed on adb device boot: [{failed_counter.adb_failed}]\n' \
                  f' - Failed on boot complete: [{failed_counter.boot_complete_failed}]\n' \
                  f' - Failed on screen on: [{failed_counter.screen_on_failed}]\n' \
                  f' - Failed camera on: [{failed_counter.camera_failed}]\n' \
                  f' - Failed on activity manager: [{failed_counter.activity_manager_failed}]\n' \
                  f' - Unknown exceptions: [{failed_counter.unknown_failed}]\n' \
                  f'    ---------------- Failed subcategory ------------------\n' \
                  f'     - CR7 error: [{failed_counter.cr7_failed}]\n' \
                  f'Average boot time: [{int(failed_counter.average_boot_time / int(TESTING_TIME))}]\n' \
                  f'{JOBURL}'

        LOGIN = "denys.horovyi@globallogic.com"
        PASSWORD = "Qwerty452++"
        TO = "denys.horovyi@globallogic.com"

        yag = yagmail.SMTP(LOGIN, PASSWORD)
        yag.send(TO, "Test Reboot Statistic", MESSAGE)

    shutil.make_archive(f'{LOG_DIR}/{request.node.name}', 'zip', testDirName)
    shutil.rmtree(testDirName)


@pytest.fixture(scope='function', autouse=False)
def logcat_logs(init_fixture):
    if init_fixture[6] == 'false':
        file_log = f'{init_fixture[7]}/logcat_{int(time.time())}.txt'
        logcatLogs = subprocess.Popen(["adb", "-s", f"{init_fixture[0]}", 'logcat'], stdout=open(file_log, 'w+'))
    else:
        pass

    yield

    try:

        logcatLogs.terminate()
    except UnboundLocalError:
        pass


@pytest.fixture(scope='function', autouse=False)
def dmesg_logs(init_fixture):
    if init_fixture[6] == 'false':
        dmesg_log = f'{init_fixture[7]}/dmesg_{int(time.time())}.txt'
        dmesgLogs = subprocess.Popen(["adb", "-s", f"{init_fixture[0]}", 'shell', 'dmesg', '-w'],
                                     stdout=open(dmesg_log, 'w+'))

    yield
    try:
        dmesgLogs.terminate()
    except UnboundLocalError:
        pass


@pytest.fixture(scope='function', autouse=False)
def serial_logger(init_fixture):
    dev = init_fixture[5]
    serial_port = serial.Serial(dev, baudrate=115200)
    file_name = f'{init_fixture[7]}/minicom_{int(time.time())}.txt'
    serial_reader = PortReader()
    serial_reader.thread_read(serial_reader.read_from_port,
                              serial_port,
                              file_name)
    yield
    serial_reader.thread_stop()


@pytest.fixture(scope='function', autouse=False)
def arduino_serial(init_fixture):
    device = init_fixture[1]
    serial_port = serial.Serial(device, baudrate=9600)
    yield serial_port
    serial_port.close()


@pytest.fixture(scope='function', autouse=False)
def cr7_logger(init_fixture):
    cr7_reader = None
    dev = init_fixture[4]
    if dev != 'None':
        serial_cr7_port = serial.Serial(dev, baudrate=115200)
        file_name = f'{init_fixture[7]}/minicom_cr7_{int(time.time())}.txt'
        cr7_reader = PortReader()
        cr7_reader.thread_read(cr7_reader.read_from_port,
                               serial_cr7_port,
                               file_name)
    else:
        pass
    yield
    try:
        cr7_reader.thread_stop()
    except Exception as e:
        print(f"Error cr7 logger wasn't run {e}")


@pytest.fixture(scope='function', autouse=False)
def ssh_pass(init_fixture):
 #write ssh_pass
    yield SSH_PASS


@pytest.fixture(scope='function', autouse=False)
def adb_serial(init_fixture) -> str:
    adb_serial = init_fixture[0]
    yield adb_serial
