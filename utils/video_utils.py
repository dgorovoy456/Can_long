import pytest
import subprocess
import time
import os


@pytest.mark.usefixtures("init_fixture")
def hdmi_image_capture(dir_to_save: str, video_input: str, file_container: str = 'png'
                       ) -> str:
    image_name = f"{dir_to_save}/screencapture_{int(time.time())}.{file_container}"
    output_path = f"{image_name}"
    capture = subprocess.Popen(
        ['ffmpeg', '-ss', '00:00:01', '-i', f"{video_input}", '-frames:v', '1', f"{image_name}"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = capture.communicate()
    assert capture.returncode == 0, "Exit code is not zero! Video wasn't recorded!"
    return output_path
