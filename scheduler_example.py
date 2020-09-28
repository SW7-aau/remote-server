import signal
import time

def interrupt_handler(signum, frame):
        print('Interrupt madafaka')
        globals()['tasks_were_completed'] = False

def wait_for_interrupt(): # Not used
    globals()['tasks_were_completed'] = True
    # Do nothing until the end of this cycle
    while (tasks_were_completed):
        time.sleep(0)

def cyclic_executives():
    MINOR_CYCLE_DURATION = 5
    signal.signal(signal.SIGALRM, interrupt_handler)
    print('Starting cycle...')
    while True:
        signal.alarm(MINOR_CYCLE_DURATION)
        wait_for_interrupt()

cyclic_executives()