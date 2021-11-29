import pytest
import allure

from utils.device_proxy import reboot_device
from utils.utils import *
from utils import failed_counter
from utils.reboot_exceptions import *
from utils.wait import *
from utils.expected_conditions import *
from utils.loggers import TestLogger
from utils.arduino_utils import arduino_enable_blue


@pytest.mark.CRT
class TestCameraReboot:

    def test_camera_reboot(self, init_fixture, arduino_serial,
                           ssh_pass):
        logger = TestLogger(scope_name=self.test_camera_reboot.__name__)
        with logger.step_log(allure.step(title='Set PCAN networking')):

            arduino_enable_blue(arduino_serial)
            time.sleep(10)
            command_set_can0 = f'echo {ssh_pass} | sudo -S ip link set can0 type can bitrate 500000'
            subprocess.Popen(command_set_can0, shell=True)
            command_setup_can0 = f'echo {ssh_pass} | sudo -S ip link set up can0'
            subprocess.Popen(command_setup_can0, shell=True)
            time.sleep(1)

            for i in range(0, int(self.REBOOT_COUNT)):
                diff_image_path_save = f"{self.camera_diff_dir}/screencapture_{int(time.time())}.png"
                current_exception = None
                minicom_log = (f'{self.testDirName}/{i}_minicom.log')

                logcat_log = (f'{self.testDirName}/{i}_logcat.log')

                ser = serial.Serial(self.USB, 115200, timeout=0)
                if not ser.isOpen():
                    ser.open()
                    wait(condition=lambda: ser.isOpen(),
                         max_timeout=30)

                ser.flushInput()
                ser.flushOutput()

                minicom_process = thread_read(read_from_port, ser, minicom_log)
                logcat_proccess = None

                start_time = time.time()
                try:
                    reboot_device(self.PHIDGET_PORT)
                    time.sleep(3)
                    # subprocess.call('/home/dhorovyi/PycharmProjects/camera/vf_test_camera/tests/camera/cam_on.sh')
                    subprocess.call('vf_test_camera/tests/camera/cam_on.sh')

                    wait(condition=lambda: self.DEVICE in adb_devices(),
                         max_timeout=180,
                         waiting_for='serial in adb devices',
                         error_msg='serial not in adb devices',
                         exception=AdbDeviceException
                         )
                    logcat_proccess = thread_read(read_from_logcat, self.DEVICE, logcat_log)
                    wait(condition=lambda: boot_complete(self.DEVICE),
                         max_timeout=60,
                         waiting_for='boot complete',
                         error_msg='boot not complete',
                         exception=BootCompleteException
                         )

                    wait(condition=lambda: awake(self.DEVICE),
                         max_timeout=60,
                         waiting_for='screen wake up',
                         error_msg='screen not wake up',
                         exception=ScreenWakeException)

                except PhidgetNotRebootException:
                    print('Phidget is broken')
                    raise PhidgetNotRebootException(f'phidget {self.PHIDGET_SERIAL} not reboot')
                except AdbDeviceException:
                    print('ADB device not found')
                    current_exception = 'adb_not_found'
                    failed_counter.adb_failed += 1
                except BootCompleteException:
                    print('Boot not completed')
                    current_exception = 'boot_complete_failed'
                    failed_counter.boot_complete_failed += 1
                except ScreenWakeException:
                    print('Screen not wake up')
                    current_exception = 'not_awake_screen'
                    failed_counter.screen_on_failed += 1
                except ActivityManagerException:
                    print('ActivityManager service did not start')
                    current_exception = 'activity_manager_not_started'
                    failed_counter.activity_manager_failed += 1
                except Exception as une:
                    print('Unknown exception' + str(une))
                    current_exception = 'unknown_failed'
                    failed_counter.unknown_failed += 1
                finally:
                    end_time = int(time.time() - start_time - 10)
                    failed_counter.average_boot_time += end_time

                    try:
                        time.sleep(15)

                        wait(condition=lambda: cameraIsEnable(self.camera_capture_dir,
                                                              self.VideoInput,
                                                              diff_image_path_save,
                                                              self.testDirName, i),
                             sleep_time=5,
                             max_timeout=30,
                             waiting_for='camera is enable',
                             error_msg='camera is disable',
                             exception=CameraExeption)
                    except CameraExeption:
                        print('Camera is disable')
                        current_exception = 'camera is not enabled'
                        failed_counter.camera_failed += 1

                    try:
                        ser.write(b'\r\n')
                        time.sleep(1)
                        ser.write(b'root\r\n')
                        time.sleep(1)
                        ser.write(b'xl list\r\n')
                        time.sleep(5)
                    except Exception as e:
                        print(e)

                    minicom_process.terminate()
                    minicom_process.join()

                    if logcat_proccess is not None:
                        logcat_proccess.terminate()
                        logcat_proccess.join()

                    if ser.isOpen():
                        ser.close()
                        time.sleep(1)

                    exception_group_checker(usb=self.USB,
                                            log_dir=self.testDirName,
                                            end_time=end_time,
                                            current_exception=current_exception,
                                            iteration=i,
                                            log_file=minicom_log)
