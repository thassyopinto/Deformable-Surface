"Deformable Surface VCM v3.0e"
"by Thassyo Pinto - thassyo@ieee.org"

# Import Standard Libraries
import math
import time

# Import External Libraries
import tkinter

# Import Local Libraries
import PCA9956B
import VCM

SFT_VRS = "v3.0e"
I2C_ADDRESS = [0x05, 0x15, 0x65]
NUM_PORT = PCA9956B.LEDDriver().nPorts
VCM_ROW = 5
VCM_MAT = VCM_ROW * VCM_ROW
VCM_SIZE = 125 # pixels
WIN_X_OFF = 0
WIN_Y_OFF = 0
WIN_X_EXT = 100
WIN_Y_EXT = 200
PWM_MIN = 0 # %
PWM_MAX = 70 # %
FREQ_MIN = 0 # Hz
FREQ_MAX = 2 # Hz
UPDATE_TIME = 10 # ms

DFT_PWM = 50
DFT_FREQ = 1

class Application(tkinter.Tk):
    def __init__(self):
        tkinter.Tk.__init__(self)
        self.title("VCM App " + SFT_VRS)
        self.frame = tkinter.Frame(self, bg='grey')
        self.frame.pack(fill='x')
        self.moveState = False
        self.ledAddress = I2C_ADDRESS
        self.systemTime = 0
        self.stopTimer = True
        self.quitTimer = False
        self.PWM_OFF = 30
        self.SIN_AMP = 20
        self.SIN_FRQ = 2
        self.SIN_PRD = 2
        # self.SIN_PHA = [0, 180, 0, 180, 0]
        # self.sineCounterStart = [0, 1.0, 0, 1.0, 0]
        # self.sineCounterEnd = [1.0, 2.0, 1.0, 2.0, 1.0]
        self.SIN_PHA = [0, 72, 144, 216, 288]
        self.sineCounterStart = [0, 0.4, 0.8, 1.2, 1.6]
        self.sineCounterEnd = [1.0, 1.4, 1.8, 2.2, 2.6]
        self.sineCounter = [0, 0, 0, 0, 0]
        self.sineDirection = [False, False, False, False, False]
        self.PWM_DC = [0, 0, 0, 0, 0]
        self.SIN_DIR = [0, 0, 0, 0, 0]
        self.createDriver()
        self.createVCM()
        self.createMenu()
        self.createCanvas()
        self.updateApp()

    def updateTime(self):
        if self.stopTimer:
            self.systemTime = 0
        else:
            # f.write(str(self.systemTime))
            # f.write(',')
            # f.write(str(self.PWM_DC[0]))
            # f.write(',')
            # f.write(str(self.PWM_DC[1]))
            # f.write(',')
            # f.write(str(self.PWM_DC[2]))
            # f.write(',')
            # f.write(str(self.PWM_DC[3]))
            # f.write(',')
            # f.write(str(self.PWM_DC[4]))
            # f.write(',')
            # f.write(str(self.SIN_DIR[0]))
            # f.write(',')
            # f.write(str(self.SIN_DIR[1]))
            # f.write(',')
            # f.write(str(self.SIN_DIR[2]))
            # f.write(',')
            # f.write(str(self.SIN_DIR[3]))
            # f.write(',')
            # f.write(str(self.SIN_DIR[4]))
            # f.write('\n')
            self.systemTime = self.systemTime + UPDATE_TIME/1000.0
            self.systemTime = round(self.systemTime, 2)
            print(self.systemTime)
            self.updateWave()
            for i in range(len(self.sineCounter)):
                self.sineCounter[i] = self.sineCounter[i] + 0.01
                self.sineCounter[i] = round(self.sineCounter[i], 2)
                # if i ==0:
                #     print(self.sineCounter[i])
                if self.sineCounter[i] >= self.sineCounterEnd[i]:
                    if self.sineDirection[i]:
                        self.sineDirection[i] = False
                        self.SIN_DIR[i] = 0
                    else:
                        self.sineDirection[i] = True
                        self.SIN_DIR[i] = 1
                    self.sineCounter[i] = self.sineCounterStart[i]


    def createDriver(self):
        self.ledDriver = []
        if not self.ledAddress:
            print("Error: No I2C addresses available!")
        else:
            for i in range(len(self.ledAddress)):
                self.ledDriver.append(PCA9956B.LEDDriver(1, self.ledAddress[i]))
                # self.ledDriver[i].begin()
                # self.ledDriver[i].setCurrent(self.ledDriver[i].allPorts, 1.0)

    def createVCM(self):
        self.vcMotor = []
        if not self.ledDriver:
            print("Error: No LED drivers available!")
        else:
            k = 0
            for i in range(len(self.ledDriver)):
                for j in range(int(NUM_PORT/2)):
                    self.vcMotor.append(VCM.Actuator())
                    self.vcMotor[k].ID = k
                    self.vcMotor[k].ADDR = i
                    self.vcMotor[k].IN1 = (j*2)
                    self.vcMotor[k].IN2 = (j*2)+1
                    self.vcMotor[k].delayTime = 1 / DFT_FREQ
                    #print(self.vcMotor[k].ADDR, self.vcMotor[k].IN1)
                    k += 1

    def createMenu(self):
        self.buttonRun = tkinter.Button(self.frame, text='Run', command=self.runApp)
        self.buttonRun.pack(side='left')
        self.buttonStop = tkinter.Button(self.frame, text='Stop', command=self.stopApp)
        self.buttonStop.pack(side='left')
        self.buttonStop = tkinter.Button(self.frame, text='SineWave', command=self.sineWave)
        self.buttonStop.pack(side='left')
        self.buttonQuit = tkinter.Button(self.frame, text='Quit', command=self.quitApp)
        self.buttonQuit.pack(side='right')

    def createCanvas(self):
        self.canvas = tkinter.Canvas(self, width=VCM_SIZE*VCM_ROW + WIN_X_EXT, height=VCM_SIZE*VCM_ROW + WIN_Y_EXT)
        self.canvas.pack()
        self.vcmBody = []
        self.vcmCheck = []
        self.vcmCheckState = []
        self.vcmPWM = []
        self.vcmPWMString = []
        self.vcmFreq = []
        self.vcmFreqString = []

        for i in range(VCM_ROW):
            for j in range(VCM_ROW):
                matrixPosition = j + (VCM_ROW * i)
                self.vcmPWMString.append(tkinter.StringVar())
                self.vcmPWMString[matrixPosition].set(DFT_PWM)
                self.vcmPWM.append(tkinter.Spinbox(self, from_=PWM_MIN, to_=PWM_MAX, width=3, textvariable=self.vcmPWMString[matrixPosition]))
                self.vcmFreqString.append(tkinter.StringVar())
                self.vcmFreqString[matrixPosition].set(DFT_FREQ)
                self.vcmFreq.append(tkinter.Spinbox(self, from_=FREQ_MIN, to_=FREQ_MAX, width=3, textvariable=self.vcmFreqString[matrixPosition]))
                self.vcmCheckState.append(tkinter.IntVar())
                self.vcmCheck.append(tkinter.Checkbutton(self, text="On/Off", variable=self.vcmCheckState[matrixPosition]))
                self.vcmBody.append(self.canvas.create_oval(VCM_SIZE * j, VCM_SIZE * i, VCM_SIZE * (j + 1), VCM_SIZE * (i + 1), fill="red"))
                self.canvas.create_text(VCM_SIZE/2 + (VCM_SIZE * j) - 40, VCM_SIZE/2 + (VCM_SIZE * i) - 10, text="PWM")
                self.canvas.create_text(VCM_SIZE/2 + (VCM_SIZE * j) + 40, VCM_SIZE/2 + (VCM_SIZE * i) - 10, text="(%)")
                self.canvas.create_window(VCM_SIZE/2 + (VCM_SIZE * j), VCM_SIZE/2 + (VCM_SIZE * i) - 10, window=self.vcmPWM[matrixPosition])
                self.canvas.create_text(VCM_SIZE/2 + (VCM_SIZE * j) - 40, VCM_SIZE/2 + (VCM_SIZE * i) + 10, text="FREQ")
                self.canvas.create_text(VCM_SIZE/2 + (VCM_SIZE * j) + 40, VCM_SIZE/2 + (VCM_SIZE * i) + 10, text="(Hz)")
                self.canvas.create_window(VCM_SIZE/2 + (VCM_SIZE * j), VCM_SIZE/2 + (VCM_SIZE * i) + 10, window=self.vcmFreq[matrixPosition])
                self.canvas.create_text(VCM_SIZE/2 + (VCM_SIZE * j), VCM_SIZE/2 + (VCM_SIZE * i) - 40, text=(j + (VCM_ROW * i) + 1), font=('Arial', 20, 'bold'))
                self.canvas.create_window(VCM_SIZE/2 + (VCM_SIZE * j), VCM_SIZE/2 + (VCM_SIZE * i) + 40, window=self.vcmCheck[matrixPosition])

        self.vcmCheckColumn = []
        self.vcmCheckColumnState = []
        self.vcmCheckRow = []
        self.vcmCheckRowState = []
        self.columnTitle = ["1","2","3","4","5"]
        self.rowTitle = ["A","B","C","D","E"]
        self.selectColumnState = []
        self.selectRowState = []

        for i in range(VCM_ROW):
            self.vcmCheckColumnState.append(tkinter.IntVar())
            self.vcmCheckRowState.append(tkinter.IntVar())
            self.vcmCheckColumn.append(tkinter.Checkbutton(self, variable=self.vcmCheckColumnState[i]))
            self.vcmCheckRow.append(tkinter.Checkbutton(self, variable=self.vcmCheckRowState[i]))
            self.canvas.create_window(VCM_SIZE/2 + (VCM_SIZE * i), VCM_SIZE*VCM_ROW + (VCM_SIZE/4), window=self.vcmCheckColumn[i])
            self.canvas.create_window(VCM_SIZE*VCM_ROW + (VCM_SIZE/4), VCM_SIZE/2 + (VCM_SIZE * i), window=self.vcmCheckRow[i])
            self.canvas.create_text(VCM_SIZE/2 + (VCM_SIZE * i), VCM_SIZE*(VCM_ROW+1) - (VCM_SIZE/2), text=self.columnTitle[i], font=('Arial', 20, 'bold'))
            self.canvas.create_text(VCM_SIZE*(VCM_ROW+1) - (VCM_SIZE/2), VCM_SIZE/2 + (VCM_SIZE * i), text=self.rowTitle[i], font=('Arial', 20, 'bold'))
            self.selectColumnState.append(0)
            self.selectRowState.append(0)

        self.rowTime = []
        self.rowTimeString = []

        for i in range(VCM_ROW):
            self.rowTimeString.append(tkinter.StringVar())
            self.rowTimeString[i].set(0)
            self.rowTime.append(tkinter.Spinbox(self, format="%.2f", increment=0.05, from_=0, to_=10, width=4, textvariable=self.rowTimeString[i]))
            self.canvas.create_window(VCM_SIZE/2 + (VCM_SIZE * i), VCM_SIZE*VCM_ROW + VCM_SIZE/1.25, window=self.rowTime[i])
            self.canvas.create_text(VCM_SIZE/2 + (VCM_SIZE * i), VCM_SIZE*(VCM_ROW+1) - (VCM_SIZE/32), text="Delay (s)", font=('Arial', 10))

        self.sinePeriodString = tkinter.StringVar()
        self.sinePeriodString.set(0)
        self.sinePeriod = tkinter.Spinbox(self, format="%.2f", increment=0.05, from_=0, to_=10, width=4, textvariable=self.sinePeriodString)
        self.canvas.create_window(VCM_SIZE*VCM_ROW + VCM_SIZE/2, VCM_SIZE*VCM_ROW + VCM_SIZE/1.25, window=self.sinePeriod)
        self.canvas.create_text(VCM_SIZE*VCM_ROW + VCM_SIZE/2, VCM_SIZE*(VCM_ROW+1) - (VCM_SIZE/2), text="P", font=('Arial', 20, 'bold'))
        self.canvas.create_text(VCM_SIZE/2 + (VCM_SIZE*VCM_ROW), VCM_SIZE*(VCM_ROW+1) - (VCM_SIZE/32), text="Period (s)", font=('Arial', 10))

        self.rowPWM = []
        self.rowPWMString = []

        for i in range(VCM_ROW):
            self.rowPWMString.append(tkinter.StringVar())
            self.rowPWMString[i].set(DFT_PWM)
            self.rowPWM.append(tkinter.Spinbox(self, from_=PWM_MIN, to_=PWM_MAX, width=3, textvariable=self.rowPWMString[i]))
            self.canvas.create_window(VCM_SIZE/2 + (VCM_SIZE * i), VCM_SIZE*(VCM_ROW+1) + VCM_SIZE/4, window=self.rowPWM[i])
            self.canvas.create_text(VCM_SIZE/2 + (VCM_SIZE * i) - 40, VCM_SIZE*(VCM_ROW+1) + VCM_SIZE/4, text="PWM")
            self.canvas.create_text(VCM_SIZE/2 + (VCM_SIZE * i) + 40, VCM_SIZE*(VCM_ROW+1) + VCM_SIZE/4, text="(%)")

        self.vcmCheckTransverseState = tkinter.IntVar()
        self.vcmCheckTransverse = tkinter.Checkbutton(self, text=" Transverse", variable=self.vcmCheckTransverseState)
        self.canvas.create_window(VCM_SIZE/3 + (VCM_SIZE*VCM_ROW), VCM_SIZE*(VCM_ROW+1) + VCM_SIZE/5, window=self.vcmCheckTransverse)

        self.selectFlipState = 0
        self.vcmCheckFlipState = tkinter.IntVar()
        self.vcmCheckFlip = tkinter.Checkbutton(self, text=" Flip", variable=self.vcmCheckFlipState)
        self.canvas.create_window(VCM_SIZE/6 + (VCM_SIZE*VCM_ROW), VCM_SIZE*(VCM_ROW+1) + VCM_SIZE/3, window=self.vcmCheckFlip)

    def runApp(self):
        self.moveState = True
        print("RUN!")
        for i in range(VCM_MAT):
            self.vcMotor[i].startClock()

    def flipDirection(self):
        self.stopTimer = True
        newCounterStart = []
        newCounterEnd = []
        newCounterStart.clear()
        newCounterEnd.clear()
        for i in range(len(self.sineCounter)-1, -1, -1):
            newCounterStart.append(self.sineCounterStart[i])
            newCounterEnd.append(self.sineCounterEnd[i])
        for i in range(len(self.sineCounter)):
            self.sineCounter[i] = 0
            self.sineDirection[i] = False
            self.sineCounterStart[i] = newCounterStart[i]
            self.sineCounterEnd[i] = newCounterEnd[i]
            print(self.sineCounterStart[i], self.sineCounterEnd[i])
        self.stopTimer = False
        print("")

    def sineWave(self):
        self.stopTimer = False
        print("SINE!")
        for i in range(len(self.sineCounter)):
            self.sineCounterStart[i] = float(self.rowTime[i].get())
            self.sineCounterEnd[i] = float(self.rowTime[i].get()) + float(self.sinePeriod.get())/2.0
            print(self.sineCounterStart[i], self.sineCounterEnd[i])

    def updateWave(self):
        for i in range(VCM_ROW):
            for j in range(VCM_ROW):
                if self.vcmCheckTransverseState.get() == 1:
                    VCM_ID = j + i*5
                else:
                    VCM_ID = j*5 + i
                #self.PWM_DC[i] =  self.PWM_OFF + self.SIN_AMP * math.sin(2 * math.pi * self.systemTime * self.SIN_FRQ + math.radians(self.SIN_PHA[i]));
                self.PWM_DC[i] = float(self.rowPWM[i].get()) / 100.0
                #print(i, self.PWM_DC[i])
                if self.sineDirection[i]:
                    self.driveMotor(self.vcMotor[VCM_ID].ADDR, self.vcMotor[VCM_ID].IN1, self.PWM_DC[i])
                    self.driveMotor(self.vcMotor[VCM_ID].ADDR, self.vcMotor[VCM_ID].IN2, 0)
                else:
                    self.driveMotor(self.vcMotor[VCM_ID].ADDR, self.vcMotor[VCM_ID].IN1, 0)
                    self.driveMotor(self.vcMotor[VCM_ID].ADDR, self.vcMotor[VCM_ID].IN2, self.PWM_DC[i])

    def stopApp(self):
        self.moveState = False
        self.stopTimer = True
        self.stopAll()
        print("STOP!")

    def quitApp(self):
        self.quitTimer = True
        self.stopApp()
        self.destroy()
        print("QUIT!")

    def driveMotor(self, addressNumber, portNumber, pwmDC):
        test = 1
        #print("DRIVING!",addressNumber,portNumber,pwmDC)
        #self.ledDriver[addressNumber].setPWM(portNumber, pwmDC)

    def stopMotor(self, motorID):
        if self.vcMotor[motorID].PWR == 1:
            self.vcMotor[motorID].PWR = 0
            self.driveMotor(self.vcMotor[motorID].ADDR, self.vcMotor[motorID].IN1, 0)
            self.driveMotor(self.vcMotor[motorID].ADDR, self.vcMotor[motorID].IN2, 0)

    def stopAll(self):
        print("STOP ALL!")
        for i in range(VCM_MAT):
            self.driveMotor(self.vcMotor[i].ADDR, self.vcMotor[i].IN1, 0)
            self.driveMotor(self.vcMotor[i].ADDR, self.vcMotor[i].IN2, 0)

    def moveVCM(self):
        if self.moveState == True:
            for i in range(VCM_MAT):
                driverPWM = float(self.vcmPWM[i].get()) / 100.0
                if self.vcmCheckState[i].get() == 1:
                    self.vcMotor[i].PWR = 1
                    self.vcMotor[i].delayTime = 1 / float(self.vcmFreq[i].get())
                    elapsedTime = time.time() - self.vcMotor[i].startTime
                    if elapsedTime >= self.vcMotor[i].delayTime:
                        self.vcMotor[i].startTime = time.time()
                        if self.vcMotor[i].DIR == 1:
                            self.vcMotor[i].DIR = 0
                            self.driveMotor(self.vcMotor[i].ADDR, self.vcMotor[i].IN1, driverPWM)
                            self.driveMotor(self.vcMotor[i].ADDR, self.vcMotor[i].IN2, 0)
                        else:
                            self.vcMotor[i].DIR = 1
                            self.driveMotor(self.vcMotor[i].ADDR, self.vcMotor[i].IN1, 0)
                            self.driveMotor(self.vcMotor[i].ADDR, self.vcMotor[i].IN2, driverPWM)
                else:
                    self.stopMotor(self.vcMotor[i].ID)

    def updateColor(self):
        for i in range(VCM_MAT):
            if self.vcmCheckState[i].get() == 1:
                self.canvas.itemconfig(self.vcmBody[i], fill='green')
            else:
                self.canvas.itemconfig(self.vcmBody[i], fill='red')

    def updateSelect(self):
        for i in range(VCM_ROW):
            if self.vcmCheckColumnState[i].get() == 1:
                self.selectColumnState[i] = 1
                for j in range(VCM_ROW):
                    self.vcmCheck[j*5 + i].select()
            else:
                if self.selectColumnState[i] == 1:
                    self.selectColumnState[i] = 0
                    for j in range(VCM_ROW):
                        self.vcmCheck[j*5 + i].deselect()

        for i in range(VCM_ROW):
            if self.vcmCheckRowState[i].get() == 1:
                self.selectRowState[i] = 1
                for j in range(VCM_ROW):
                    self.vcmCheck[j + i*5].select()
            else:
                if self.selectRowState[i] == 1:
                    self.selectRowState[i] = 0
                    for j in range(VCM_ROW):
                        self.vcmCheck[j + i*5].deselect()

        if self.vcmCheckFlipState.get() == 1:
            if self.selectFlipState == 0:
                self.selectFlipState = 1
                self.flipDirection()
        else:
            if self.selectFlipState == 1:
                self.selectFlipState = 0
                self.flipDirection()

    def updateApp(self):
        self.updateSelect()
        self.updateColor()
        self.moveVCM()
        self.updateTime()
        self.after(UPDATE_TIME, self.updateApp)


if __name__=="__main__":
    app = Application()
    app.mainloop()
