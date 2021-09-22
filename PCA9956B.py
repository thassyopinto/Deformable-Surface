"PCA9956B Library v1.0"
"by Thassyo Pinto - thassyo@ieee.org"

#!/usr/bin/python

#from smbus import SMBus
from enum import Enum

class LEDDriver:
    def __init__(self, i2cChannel = 1, i2cAddress = 0x3F):
        self.i2cAddress = i2cAddress
        self.i2cChannel = i2cChannel
        self.allPorts = 0xFF
        self.nPorts = 24

    class REG_DEF(Enum):
        MODE1 = 0x00
        MODE2 = 0x01
        LEDOUT0 = 0x02
        LEDOUT1 = 0x03
        LEDOUT2 = 0x04
        LEDOUT3 = 0x05
        LEDOUT4 = 0x06
        LEDOUT5 = 0x07
        GRPPWM = 0x08
        GRPFREQ = 0x09
        PWM0 = 0x0A
        PWM1 = 0x0B
        PWM2 = 0x0C
        PWM3 = 0x0D
        PWM4 = 0x0E
        PWM5 = 0x0F
        PWM6 = 0x10
        PWM7 = 0x11
        PWM8 = 0x12
        PWM9 = 0x13
        PWM10 = 0x14
        PWM11 = 0x15
        PWM12 = 0x16
        PWM13 = 0x17
        PWM14 = 0x18
        PWM15 = 0x19
        PWM16 = 0x1A
        PWM17 = 0x1B
        PWM18 = 0x1C
        PWM19 = 0x1D
        PWM20 = 0x1E
        PWM21 = 0x1F
        PWM22 = 0x20
        PWM23 = 0x21
        IREF0 = 0x22
        IREF1 = 0x23
        IREF2 = 0x24
        IREF3 = 0x25
        IREF4 = 0x26
        IREF5 = 0x27
        IREF6 = 0x28
        IREF7 = 0x29
        IREF8 = 0x2A
        IREF9 = 0x2B
        IREF10 = 0x2C
        IREF11 = 0x2D
        IREF12 = 0x2E
        IREF13 = 0x2F
        IREF14 = 0x30
        IREF15 = 0x31
        IREF16 = 0x32
        IREF17 = 0x33
        IREF18 = 0x34
        IREF19 = 0x35
        IREF20 = 0x36
        IREF21 = 0x37
        IREF22 = 0x38
        IREF23 = 0x39
        OFFSET = 0x3A
        SUBADR1 = 0x3B
        SUBADR2 = 0x3C
        SUBADR3 = 0x3D
        ALLCALLADR = 0x3E
        PWMALL = 0x3F
        IREFALL = 0x40
        EFLAG0 = 0x41
        EFLAG1 = 0x42
        EFLAG2 = 0x43
        EFLAG3 = 0x44
        EFLAG4 = 0x45
        EFLAG5 = 0x46
        REG_START           = 0x00
        REG_START_LEDOUT    = 0x02
        REG_START_PWM       = 0x0A
        REG_START_IREF      = 0x22

    class MODE1_BITS(Enum):
        MODE1_ALLCALL = 0x00
        MODE1_SUB3 = 0x01
        MODE1_SUB2 = 0x02
        MODE1_SUB1 = 0x03
        MODE1_SLEEP = 0x04
        MODE1_AI0 = 0x05
        MODE1_AI1 = 0x06
        MODE1_AIF = 0x07

    class MODE2_BITS(Enum):
        MODE2_OCH = 0x03
        MODE2_CLRERR = 0x04
        DMBLNK = 0x05
        ERROR = 0x06
        OVERTEMP = 0x07

    def begin(self):
        self.bus = SMBus(self.i2cChannel)
        initialize()

    def initialize(self):
        writeByte(self.REG_DEF.MODE1.value, 0x00)
        writeByte(self.REG_DEF.MODE2.value, 0x00)

    def setPWM(self, portNumber, dutyCycle):
        regNumber = self.REG_DEF.PWMALL.value;
        if portNumber < self.nPorts:
            regNumber = self.REG_START_PWM + portNumber
        writeByte(regNumber, int(dutyCycle * 255.0))

    def setCurrent(self, portNumber, percentValue):
        regNumber = self.REG_DEF.IREFALL.value;
        if portNumber < self.nPorts:
            regNumber = self.REG_START_IREF + portNumber
        writeByte(regNumber, int(percentValue * 255.0))

    def writeByte(self, regNumber, data):
        self.bus.write_byte_data(self.i2cAddress, regNumber, data)
