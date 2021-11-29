import multiprocessing
import time
import serial
import os


class PortReader:
    RUNNER = True

    def read_from_port(self, ser: serial.Serial,
                       file_name: str
                       ):
        file = open(file_name, "ab")
        with ser, file:
            try:
                while self.RUNNER:
                    time.sleep(1)
                    try:
                        file.write(ser.read(ser.inWaiting()))
                        file.flush()
                    except serial.SerialException as se:
                        print(f'Serial exception: {se}')
            except Exception as e:
                print(f'Read from port exception: {e}')
            finally:
                print('Close file')
                file.close()

    def thread_read(self, target, ser, file_name):
        self.proc = multiprocessing.Process(target=target, args=(ser, file_name))
        self.proc.start()
        return self.proc

    def thread_stop(self):
        self.RUNNER = False
        self.proc.terminate()
        self.proc.join(1)

        try:
            os.kill(self.proc.pid, 9)
        except Exception as e:
            print(f'Proccess error {e}')
