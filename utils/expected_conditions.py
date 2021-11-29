import subprocess
import os
import time
import shutil

from utils.video_utils import hdmi_image_capture
from utils.image_utils import compare_images


def adb_devices() -> str:
    return subprocess.check_output("adb devices".split()).decode()


def boot_complete(serial: str) -> bool:
    try:
        return bool(subprocess.check_output(f"adb -s {serial} shell getprop sys.boot_completed".split()).decode())
    except:
        return False


def awake(serial: str) -> bool:
    try:
        output = subprocess.check_output(f"adb -s {serial} shell dumpsys window | grep 'mAwake'".split()).decode()
        if 'mAwake=true' in output:
            return True
    except:
        return False


def activity_manager(serial: str) -> bool:
    try:
        output = subprocess.check_output(f"adb -s {serial} shell service check activity".split()).decode()
        if 'Service activity: found' in output:
            return True
    except:
        return False


def cameraIsEnable(cam_cap_dir: str, VideoInput: str, diff_im_pass_save: str, testDirName: str, i: int) -> bool:
    capture = None
    if i == 0:
        capture1 = hdmi_image_capture(cam_cap_dir, VideoInput, 'png')
        image1 = shutil.copy(capture1, f'{testDirName}/sample1.png')
        time.sleep(3)
        os.remove(capture1)
    else:
        image1 = f'{testDirName}/sample1.png'
        capture = hdmi_image_capture(cam_cap_dir, VideoInput, 'png')
    if i != 0:
        sample_image = image1
        score = compare_images(sample_image, capture, diff_im_pass_save)
        print(score)

        if score > 0.89:
            os.remove(capture)
            os.remove(diff_im_pass_save)
            return True
        else:
            os.remove(diff_im_pass_save)
            return False
    else:
        return True
