import time

from datetime import datetime
from typing import Callable


def wait(condition: Callable,
         max_timeout: int or float = 10,
         sleep_time: int or float = 0.5,
         waiting_for: str = '',
         error_msg: str = '',
         fail: bool = False,
         xfail: bool = False,
         exception=Exception):
    """
    condition = callable or 'lambda: some_value'
    """
    start_time = time.time()
    while not condition():
        time_delta = time.time() - start_time

        time.sleep(sleep_time)
        if time_delta > max_timeout:
            raise exception(f'{error_msg} {time_delta}')
    message = f'Waiting for {waiting_for}... {int((time.time() - start_time))}'
    print(message)
