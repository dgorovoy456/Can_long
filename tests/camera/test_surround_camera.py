import os
import shutil
import allure
import delayed_assert
import subprocess
import time
import pytest
import uiautomator2

from conftest import LOG_DIR
from utils.video_utils import hdmi_image_capture
from utils.loggers import TestLogger
from utils.image_utils import compare_images
from utils.device_proxy import reboot_device
from utils.arduino_utils import arduino_enable_blue, arduino_enable_red


class TestCameraSurround:

    @pytest.mark.SCT
    def test_surround_camera_test_with_record(self, init_fixture,
                                              logcat_logs,
                                              dmesg_logs,
                                              serial_logger,
                                              cr7_logger,
                                              arduino_serial,
                                              ssh_pass,
                                              adb_serial
                                              ):
        CAMERA_BUTTON = {'resourceId': 'com.vinfast.ivi.launcher:id/btn_quick_control_camera'}
        CAMERA_EXIT_BUTTON = {'resourceId': 'com.vinfast.android.evs:id/xButton'}
        CAMERA_VIEW = {'resourceId': 'com.vinfast.android.evs:id/relativeLayout'}

        logger = TestLogger(scope_name=self.test_surround_camera_test_with_record.__name__)
        with logger.step_log(allure.step(title='Reboot DUT')):
            if self.PCan == 'true':
                logger = TestLogger(scope_name=self.test_surround_camera_test_with_record.__name__)
                reboot_device(self.PHIDGET_PORT)
                time.sleep(50)
                file_log = f'{self.testDirName}/logcat_{int(time.time())}.txt'
                logcatLogs = subprocess.Popen(["adb", "-s", f"{self.DEVICE}", 'logcat'],
                                              stdout=open(file_log, 'w+'))
                dmesg_log = f'{self.testDirName}/dmesg_{int(time.time())}.txt'
                dmesgLogs = subprocess.Popen(["adb", "-s", f"{self.DEVICE}", 'shell', 'dmesg', '-w'],
                                             stdout=open(dmesg_log, 'w+'))
            else:
                pass

        for i in range(0, int(self.TESTING_TIME)):
            diff_image_path_save = f"{self.camera_diff_dir}/screencapture_{int(time.time())}.png"
            file_log = f'{LOG_DIR}/logcat_full_.txt'

            with logger.step_log(allure.step(title='Enable the surround camera')):
                pass
                ui = uiautomator2.connect_usb(adb_serial, init=False)
                ui.sleep(5)
                ui(**CAMERA_BUTTON).click()
                ui.sleep(5)

            with logger.step_log(allure.step(title='Start image capture')):

                if i == 0:
                    time.sleep(5)
                    arduino_enable_blue(arduino_serial)
                    time.sleep(3)
                    capture1 = hdmi_image_capture(self.camera_capture_dir, self.VideoInput, 'png')
                    image1 = shutil.copy(capture1, f'{self.testDirName}/sample1.png')
                    time.sleep(3)
                    os.remove(capture1)
                    arduino_enable_red(arduino_serial)
                    time.sleep(3)
                    capture2 = hdmi_image_capture(self.camera_capture_dir, self.VideoInput, 'png')
                    image2 = shutil.copy(capture2, f'{self.testDirName}/sample2.png')
                    time.sleep(3)
                    os.remove(capture2)

                if i % 2 == 0:
                    arduino_enable_blue(arduino_serial)
                    time.sleep(1)
                    capture = hdmi_image_capture(self.camera_capture_dir, self.VideoInput, 'png')
                else:
                    arduino_enable_red(arduino_serial)
                    time.sleep(1)
                    capture = hdmi_image_capture(self.camera_capture_dir, self.VideoInput, 'png')

            with logger.step_log(allure.step(title='Check similarity images')):
                if i % 2 == 0:
                    sample_image = image1
                else:
                    sample_image = image2
                score = compare_images(sample_image, capture, diff_image_path_save)
                delayed_assert.expect(score > 0.89,
                                      f"Captured image is not expected! "
                                      f"Actual simularity - {score}, expected 0.9, count - {i}")
                if score > 0.89:
                    os.remove(capture)
                    os.remove(diff_image_path_save)

                if score < 0.89:
                    logcat_logs.terminate()
                    try:

                        logcatLogsFull = subprocess.Popen(["adb", "-s", f"{self.DEVICE}", 'logcat', '*:W'],
                                                          stdout=open(file_log, 'w+'))
                    except FileExistsError as logcatLogsFull:
                        pass

            time.sleep(30)

        try:
            logcatLogsFull.terminate()
        except UnboundLocalError:
            pass

        if self.PCan == 'true':
            try:
                logcatLogs.terminate()
                dmesgLogs.terminate()
            except UnboundLocalError:
                pass

        # coordinates = [584, 64, 1336, 904]

        with logger.step_log(allure.step(title='Get camera view coordinate')):
            b = [ui(**CAMERA_VIEW).bounds()]
            time.sleep(5)
            ui(**CAMERA_EXIT_BUTTON).click()
            print(b)

        with logger.step_log(allure.step(title='Check delayed assertions...')):
            pass
            delayed_assert.assert_expectations()
