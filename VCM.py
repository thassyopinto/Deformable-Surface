"VCM Object v1.0"
"by Thassyo Pinto - thassyo@ieee.org"

import time

class Actuator():
    def __init__(self):
        self.ID = 0
        self.ADDR = 0
        self.IN1 = 0
        self.IN2 = 0
        self.DIR = 0
        self.PWR = 0
        self.startTime = 0
        self.delayTime = 0.5

    def startClock(self):
        self.startTime = time.time()
