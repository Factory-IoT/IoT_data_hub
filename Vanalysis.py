# use M5StickC and "m5stickc_accelerometer" ver1.0.0 or higher
# Ver 001 add FFT analysis menu
# Ver 002 add FFT data save, FFT analyze only
# Ver 010 add data load func, status monitor
# Ver 011 remove DC components, adjusted the graph.
# Ver 100 git commit

import subprocess
import serial
import csv
import numpy as np
import matplotlib.pyplot as plt

BT = False
MAC_ADDRESS = "D8:A0:1D:55:27:7A"
DIR = "/home/pi/workspace/"
DATA_FILE = "accel_data"
FFT_FILE = "FFT_data"

if BT == True:
    res = subprocess.check_call(["sudo","rfcomm","bind","1", MAC_ADDRESS])
    ser=serial.Serial("/dev/rfcomm1",115200,timeout=None)
    ser.close()

samplingTime = []
ax = []
ay = []
az = []
ampx = []
ampy = []
ampz = []
freq = []

mesureNum = 0
sampleSize = 0

def data_save():

    for i in range(mesureNum):
        dataSet = []
        dataSet.append(samplingTime[i])
        dataSet.append(ax[i])
        dataSet.append(ay[i])
        dataSet.append(az[i])
        dataSet = np.array(dataSet).T.tolist()
        
        with open(DATA_FILE + str(i) + '.csv',mode = 'w') as f:
            writer = csv.writer(f)
            writer.writerows(dataSet)

def data_load():

    print('data load')
    global samplingTime
    global ax
    global ay
    global az
    global mesureNum
    global sampleSize
    samplingTime = []
    ax = []
    ay = []
    az = []
    ampx.clear()
    ampy.clear()
    ampz.clear()
    mesureNum = int(input("input number of data > "))
        
    for i in range(mesureNum):
        with open(DATA_FILE + str(i) + ".csv") as f:
            reader = csv.reader(f)
            dataSet = [row for row in reader]
            dataSet = np.array(dataSet).T.tolist()
            dataSet = [[float(item) for item in row] for row in dataSet]
            samplingTime.append(dataSet[0])
            ax.append(dataSet[1])
            ay.append(dataSet[2])
            az.append(dataSet[3])
            sampleSize = len(ax[i])

def FFT_data_save():
    print('FFT data save')
    
    for i in range(len(freq)):
        dataSet = []
        dataSet.append(freq[i])
        dataSet.append(ampx[i])
        dataSet.append(ampy[i])
        dataSet.append(ampz[i])
        dataSet = np.array(dataSet).T.tolist()
        
        with open(FFT_FILE + str(i) + '.csv',mode = 'w') as f:
            writer = csv.writer(f)
            writer.writerows(dataSet)

def recieve_mode():
    if BT == True:
        global samplingTime
        global ax
        global ay
        global az
        global mesureNum
        global sampleSize
        samplingTime = []
        ax = []
        ay = []
        az = []

        ser.open()
        ser.reset_input_buffer()
        ser.reset_output_buffer()
    
        print("")
        print("Push M5StickC BtnB.")
        BTcheck_raw = ser.readline()
        BTcheck = int(repr(BTcheck_raw.decode())[1:-5])

        if (BTcheck == 255):
            BTcheckBi = bytes([BTcheck])
            ser.write(BTcheckBi)
    
            sampleSizeRaw = ser.readline()
            sampleSize = int(repr(sampleSizeRaw.decode())[1:-5])
    
            mesureNumRaw = ser.readline()
            mesureNum = int(repr(mesureNumRaw.decode())[1:-5])
    
            print("sampleSize = " + str(sampleSize))
            print("mesureNum = " + str(mesureNum))
            print("data recieving." , end = "")
       
            for i in range(mesureNum):
                ax_row = []
                ay_row = []
                az_row = []         
                samplingTime_row = []
            
                for j in range(sampleSize):
                    if j % 500 == 1:
                        print("." , end = "")                
                    samplingTime_data = ser.readline()
                    if j == 0:
                        samplingTime_row.append(float(repr(samplingTime_data.decode())[1:-5]))                    
                    if j > 0:
                        samplingTime_row.append(float(repr(samplingTime_data.decode())[1:-5]) + samplingTime_row[j - 1])
                    ax_data = ser.readline()
                    ay_data = ser.readline()
                    az_data = ser.readline()
                    ax_row.append(float(repr(ax_data.decode())[1:-5]))
                    ay_row.append(float(repr(ay_data.decode())[1:-5]))
                    az_row.append(float(repr(az_data.decode())[1:-5]))

                ax.append(ax_row)
                ay.append(ay_row)
                az.append(az_row)
                samplingTime.append(samplingTime_row)

        ser.close()
        print("")
        
    else:
        print('local mode')

def view_raw_data():
    print("raw_data")    
    print(samplingTime)
    print(az)
    for i in range(mesureNum):
        for j in range(sampleSize):
            print(str(i) + '-' + str(j) + ' , time = ' + str(samplingTime[i][j]) + ' , ax = ' + str(ax[i][j]) + ' , ay = ' + str(ay[i][j]) + ' , az = ' + str(az[i][j]))

def view_raw_data_graph():
    print("")
    print("graph mode")
    print("Input axis. ('x' or 'y' or 'z')")
    x = input(">")

    if x == "x":
        print("x axis")
        for i in range(mesureNum):
            plt.plot(samplingTime[i],ax[i])
        
    elif x == "y":
        print("y axis")
        for i in range(mesureNum):
            plt.plot(samplingTime[i],ay[i])

    elif x == "z":
        print("z axis")
        for i in range(mesureNum):
            plt.plot(samplingTime[i],az[i])
    else:
        print("command " + x + " is not defined.")

    plt.show()

def FFTmenu():
    print("")
    print("FFT mode")
    
    if mesureNum == 0:
        print("     ...no data")
        
    else:
        print("Input sample number 0 - ", end = "")
        print(mesureNum - 1, end = "")
        print(", draw graphs. Input 99, analayze only.") 
        x = int(input(">"))
        
        if x >= 0 and x < mesureNum :
            print("Sample ", end = "")
            print(x, end = "")
            print(" is selected.")
            FFT(x)
            
        elif x == 99:
            FFT(x)

        else:
            print("Sample ", end = "")
            print(x, end = '')
            print(" does not exist.")

def FFT(i):
    global ampx
    global ampy
    global ampz
    global freq
    ampx.clear()
    ampy.clear()
    ampz.clear()
    dt = []
    t = []
    
    for j in range (mesureNum):
        dtime = (samplingTime[j][sampleSize - 1] / sampleSize ) / 1000000 
        dt.append(dtime)
        
        time = np.arange(0, sampleSize * dt[j], dt[j])
        t.append(time)
        
        f = np.linspace(0, 1.0/dt[j], sampleSize)
        freq.append(f.tolist())
        
        meanx = sum(ax[j])/len(ax[j])
        meany = sum(ay[j])/len(ay[j])
        meanz = sum(az[j])/len(az[j])
        
        ax[j] = [n - meanx for n in ax[j]]
        ay[j] = [n - meany for n in ay[j]]
        az[j] = [n - meanz for n in az[j]]
        
        
        Fx = np.fft.fft(ax[j])
        Fy = np.fft.fft(ay[j])
        Fz = np.fft.fft(az[j])
        
        ndarrx = np.abs(Fx)
        ndarry = np.abs(Fy)
        ndarrz = np.abs(Fz)
        
        ampx.append(ndarrx.tolist())
        ampy.append(ndarry.tolist())
        ampz.append(ndarrz.tolist())
        
    if i != 99:
        
        plt.figure(figsize = (18.0, 12.0), dpi = 100)
        plt.subplot(321)
        plt.plot(t[i], ax[i], label = "fx(n)")
        plt.xlabel("Time(sec)")
        plt.ylabel("Signal(mG)")
 
        plt.subplot(323)
        plt.plot(t[i], ay[i], label = "fy(n)")
        plt.xlabel("Time(sec)")
        plt.ylabel("Signal(mG)")

        plt.subplot(325)
        plt.plot(t[i], az[i], label = "fz(n)")
        plt.xlabel("Time(sec)")
        plt.ylabel("Signal(mG)")
        
        plt.subplot(322)
        plt.plot(freq[i], ampx[i], label = "|Fx(k)|")
        plt.xlabel("Frequency(Hz)")
        plt.ylabel("Amplitude")
    
        plt.subplot(324)
        plt.plot(freq[i], ampy[i], label = "|Fy(k)|")
        plt.xlabel("Frequency(Hz)")
        plt.ylabel("Amplitude")
    
        plt.subplot(326)
        plt.plot(freq[i], ampz[i], label = "|Fz(k)|")
        plt.xlabel("Frequency(Hz)")
        plt.ylabel("Amplitude")
    
        plt.show()   
    
def menu():
    print("")
    print("= data status ============")
    print("  number of data   :", end = "")
    print(mesureNum)
    print("  data size        :", end = "")
    print(sampleSize)
    print("  FFT analisys     :", end = "")
    print(len(ampx) != 0)
    print("")
    print("= command list ===========")
    print("1:data recieve mode")
    print("2:view raw data")
    print("3:view raw data graph")
    print("4:FFT analisys")
    print("5:save raw data")
    print("6:save FFT data")
    print("7:load raw data")
    print("q:quit")
    print("")
    x = input("input command > ")

    if x == "1":
        print("command 1 selected")
        recieve_mode()

    elif x == "2":
        print("command 2 selected")
        view_raw_data()
        
    elif x == "3":
        print("command 3 selected")
        view_raw_data_graph()

    elif x == "4":
        print("command 4 selected")
        FFTmenu()
    
    elif x == "5":
        print("command 5 selected")
        data_save()
        
    elif x == "6":
        print("command 6 selected")
        FFT_data_save()
    
    elif x == "7":
        print("command 7 selected")
        data_load()
        
        
    elif x == "l":
        print([len(v) for v in ax])
        print([len(v) for v in ay])
        print([len(v) for v in az])
        print([len(v) for v in samplingTime])

    elif x == "q":
        return 99
    
    else:
        print("command " + x + " is not defined.")

while True:
    result = menu()
    if result == 99:
        break
print("break")
