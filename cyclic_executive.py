import signal
import time

import read_processes
import read_resources


class CyclicExecutive:
    def __init__(self, verbosity=0, cycle_duration=5, send_frequency=6,
                 function=''):
        self.verbosity = verbosity
        self.cycle_duration = cycle_duration
        self.send_frequency = send_frequency
        self.function = function

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
            if self.function == 'get_resources':
                getattr(read_resources, self.function)()
                if self.verbosity == 1:
                    print('Resources read')
                if counter % self.send_frequency == 0:
                    getattr(read_resources, 'send_resources_list')()
                    if self.verbosity == 1:
                        print('Resources sent')
            elif self.function == 'get_processes':
                getattr(read_processes, self.function)()
                if self.verbosity == 1:
                    print('Processes read')
                if counter % self.send_frequency == 0:
                    getattr(read_processes, 'send_processes_list')()
                    if self.verbosity == 1:
                        print('Processes sent')
            counter = counter + 1
            self.wait_for_interrupt()
