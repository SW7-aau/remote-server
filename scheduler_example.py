import signal
import time

import read_resources


def interrupt_handler(signum, frame):
        print('Interrupt madafaka')
        globals()['tasks_were_completed'] = False


def wait_for_interrupt(): # Not used
    globals()['tasks_were_completed'] = True
    # Do nothing until the end of this cycle
    while (tasks_were_completed):
        time.sleep(0)


def cyclic_executives():
    minor_cycle_duration = 5
    timer = 0
    signal.signal(signal.SIGALRM, interrupt_handler)
    print('Starting cycle...')
    while True:
        signal.alarm(minor_cycle_duration)
        read_resources.get_resources()
        print("Resources read")
        if timer % 6 == 0:
            read_resources.send_resources_list()
            print("Resources sent")
        timer = timer + 1
        wait_for_interrupt()


cyclic_executives()
