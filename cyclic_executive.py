import signal
import time

#Scheduler class to be instantiated as part of an application
#Arguments given by said application.
#getattr is used to access those functions, with function 1 always being a getter while function 2 is a sender.
class CyclicExecutive:
    def __init__(self, verbosity, cycle_duration, send_frequency,
                 functions):
        """
        :param verbosity: If scheduler should be verbose
        :param cycle_duration: How often functions[1] should be called
        :param send_frequency: How often functions[1] should be called before
                                functions[2]
        :param functions: The module and functions names
        """
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
        signal.pause()

    def job(self, counter):
        #Read metrics
        getattr(self.functions[0], self.functions[1])()
        if self.verbosity == 1:
            print('Resources read')
        
        #Send Metrics
        if counter % self.send_frequency == 0:
            getattr(self.functions[0], self.functions[2])()
            if self.verbosity == 1:
                print('Resources sent')

    def run(self):
        counter = 1
        signal.signal(signal.SIGALRM, self.interrupt_handler)
        if self.verbosity == 1:
            print('Starting cycle...')
        while True:
            signal.alarm(self.cycle_duration)
            self.job(counter)
            counter = counter + 1
            self.wait_for_interrupt()
