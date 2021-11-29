import subprocess


def camera_on():
    pass
    with open('/home/dhorovyi/PycharmProjects/camera/vf_test_camera/tests/camera/rcv_cam_on.log', 'r') as file:
        line = file.readlines()

        for l in line:
            value1 = l.replace(" ", '')
            if value1[8] == '8':
                value2 = value1.replace('[8]', '#')
            else:
                value2 = value1.replace('[3]', '#')
            value3 = value2[:4] + ' ' + value2[4:]
            command_set_can0 = f'cansend {value3}'
            subprocess.Popen(command_set_can0, shell=True)
