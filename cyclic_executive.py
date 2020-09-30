import signal
import time

import read_processes
import read_resources


class CyclicExecutive:
    def __init__(self, verbosity=0, cycle_duration=5, send_frequency=6,
                 func1='', func2=''):
        self.verbosity = verbosity
        self.cycle_duration = cycle_duration
        self.send_frequency = send_frequency
        self.func1 = func1
        self.func2 = func2

    def interrupt_handler(self, signum, frame):
        if self.verbosity == 1:
            print("Interrupt")
        globals()['tasks_completed'] = False

    def wait_for_interrupt(self):
        globals()['tasks_completed'] = True
        while globals()['tasks_completed']:
            time.sleep(0)

    def run(self):
        counter = 1
        signal.signal(signal.SIGALRM, self.interrupt_handler)
        if self.verbosity == 1:
            print('Starting cycle...')
        while True:
            signal.alarm(self.cycle_duration)
            if self.func1 == 'get_resources':
                getattr(read_resources, self.func1)()
                if self.verbosity == 1:
                    print('Resources read')
                if counter % self.send_frequency == 0:
                    getattr(read_resources, self.func2)()
                    if self.verbosity == 1:
                        print('Resources sent')
            elif self.func1 == 'get_processes':
                getattr(read_processes, self.func1)()
                if self.verbosity == 1:
                    print('Processes read')
                if counter % self.send_frequency == 0:
                    getattr(read_processes, self.func2)()
                    if self.verbosity == 1:
                        print('Processes sent')
            counter = counter + 1
            self.wait_for_interrupt()
