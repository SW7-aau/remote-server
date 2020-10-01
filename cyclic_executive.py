import signal
import time

import read_processes
import read_resources


class CyclicExecutive:
    def __init__(self, verbosity=0, cycle_duration=5, send_frequency=6,
                 functions=[]):
        self.verbosity = verbosity
        self.cycle_duration = cycle_duration
        self.send_frequency = send_frequency
        self.functions = functions
        self.task_completed = False

    def interrupt_handler(self, signum, frame):
        if self.verbosity == 1:
            print("Interrupt")
        self.task_completed = False

    def wait_for_interrupt(self):
        self.task_completed = True
        while self.task_completed:
            time.sleep(0)

    def run(self):
        counter = 1
        signal.signal(signal.SIGALRM, self.interrupt_handler)
        if self.verbosity == 1:
            print('Starting cycle...')
        while True:
            signal.alarm(self.cycle_duration)
            getattr(self.functions[0], self.functions[1])()
            if self.verbosity == 1:
                print('Resources read')
            if counter % self.send_frequency == 0:
                getattr(self.functions[0], self.functions[2])()
                if self.verbosity == 1:
                    print('Resources sent')
            counter = counter + 1
            self.wait_for_interrupt()
