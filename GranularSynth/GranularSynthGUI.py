# Alexander Freer
# 6452551

# Alec Ames
# 6843577

# Granular Synthesis Engine

import sys
import random
from tqdm import tqdm
from PyQt5.QtWidgets import QApplication, QWidget, QSlider, QVBoxLayout, QLabel, QPushButton, QFileDialog, QProgressBar
from PyQt5.QtCore import Qt

# set input location
def set_in ():
    global inFileName
    inFileName = QFileDialog.getOpenFileName()[0]
    inputLabel.setText(inFileName)

# set save locatioN
def set_out (): 
    global outFileName
    outFileName = QFileDialog.getSaveFileName()[0]
    outputLabel.setText(outFileName)

def tone_convert(origArr, phsIdx, dur, stepSize):
    newArr = []

    i = phsIdx
    count = 0
    while count < dur:
        tblVal = int(i) % len(origArr)
        rem = i % 1
        newVal = 0

        tblVal1 = float(origArr[tblVal])
        tblVal2 = float(origArr[(tblVal+1) % len(origArr)])
        newVal = tblVal1 + (rem * (tblVal2-tblVal1))

        newArr.append(newVal)

        i = i + (2 ** (stepSize/12))
        count += 1

    return newArr

def compute_grain(grainSize, samples, pitch):
    grain = []

    i = int(random.random()*(len(samples)-grainSize))

    for j in range(grainSize):
        grain.append(samples[j+i])
    
    grain = tone_convert(grain, 0, grainSize, pitch)

    for j in range(len(grain)):
        # ramp up from 0 to 1/4 of grainSize
        # top from 1/4-3/4
        # ramp down from 3/4 to 1
        envelope = float(0)
        upRamp = int((1/4)*grainSize)
        downRampStart = int((3/4)*grainSize)
        if j <= upRamp:
            envelope = j/upRamp
        elif j < downRampStart:
            envelope = 1
        else:
            envelope = 1-(j/upRamp)
        grain[j] = grain[j] * envelope
            
    return grain

def save_file (outFileName, samples):
    with open(outFileName, 'w') as outFile:
        for sample in samples:
            outFile.write(str(sample) + '\n')

def run_granular():
    SAMPLERATE = 44100
    grainDur = grainDurSlider.value() #should be between 1ms-100ms
    grainGenRate = grainGenRateSlider.value() # grains/second
    pitch = pitchSlider.value() #grain pitch
    location = locationSlider.value()  #min and max locations from center, from which grains are generated (.8 means 80% thus, no grains in first 10% and final 10% of audio)
    outputDuration = outputDurationSlider.value() #seconds

    origFile = open(inFileName, "r")
    newFile = open(outFileName, "w")

    samples = origFile.readlines()
    samples = list(map(lambda n: float(n), samples))

    p = 1 - location
    start = int(len(samples)*(p/2))
    end = int(len(samples) - start)

    #trim sample list to get start and end index
    samples = samples[start:end]

    outputBuffer = [0] * (outputDuration * SAMPLERATE) #initialize output buffer with 0's

    # pad the input samples with 0's if output is longer
    if len(outputBuffer) > len(samples) :
        samples += [0] * (len(outputBuffer) - len(samples))

    probability = grainGenRate / SAMPLERATE
    grainSize = int((grainDur / 1000) * SAMPLERATE)

    for i in tqdm(range(len(outputBuffer))):
        if random.random() < probability:
            # Prevent buffer overflowS
            if grainSize >= (len(outputBuffer) - i):
                grainSize = (len(outputBuffer) - i)-1
            grain = compute_grain(grainSize, samples, pitch)
            for j in range(len(grain)):
                outputBuffer[i+j] = outputBuffer[i+j] + (0.5*grain[j])
                # Preventing clipping
                if (outputBuffer[i+j] < 0):
                    outputBuffer[i+j] = max(outputBuffer[i+j], -1)
                else:
                    outputBuffer[i+j] = min(outputBuffer[i+j], 1)
        progressBar.setValue(i/len(outputBuffer)*100)

    save_file(outFileName, outputBuffer)
    origFile.close()
    newFile.close()
    
    progressBar.setValue(100)

# setup gui
app = QApplication([])
window = QWidget()
window.setWindowTitle('Granular Synthesis Engine')

inFileName = ""
outFileName = ""

# add file
inputLabel = QLabel("Choose a file to open")
openFileButton = QPushButton('Load File')
openFileButton.clicked.connect(set_in)

# set output file location
outputLabel = QLabel("Choose a file to save to")
setOutButton = QPushButton ('Set Output')
setOutButton.clicked.connect(set_out)

# slider for grain duration
grainDurSlider = QSlider(orientation=Qt.Horizontal)
grainDurLabel = QLabel('Grain duration (ms): 100')
grainDurSlider.setRange(1, 250)
grainDurSlider.setValue(100)
grainDurSlider.valueChanged.connect(lambda: grainDurLabel.setText('Grain duration (ms): ' + str(grainDurSlider.value())))

# slider for grain density
grainGenRateSlider = QSlider(orientation=Qt.Horizontal)
grainGenRateLabel = QLabel('Grain generation rate: 200')
grainGenRateSlider.setRange(1, 1000)
grainGenRateSlider.setValue(200)
grainGenRateSlider.valueChanged.connect(lambda: grainGenRateLabel.setText('Grain generation rate: ' + str(grainGenRateSlider.value())))

# slider for pitch
pitchSlider = QSlider(orientation=Qt.Horizontal)
pitchLabel = QLabel('Pitch (semitones): 0')
pitchSlider.setRange(-24, 24)
pitchSlider.setValue(0)
pitchSlider.valueChanged.connect(lambda: pitchLabel.setText('Pitch (semitones): ' + str(pitchSlider.value())))

# slider for location
locationSlider = QSlider(orientation=Qt.Horizontal)
locationLabel = QLabel('Location (position in audio): 80')
locationSlider.setRange(0, 100)
locationSlider.setValue(80)
locationSlider.valueChanged.connect(lambda: locationLabel.setText('Location (position in audio): ' + str(locationSlider.value())))

# slider for duration
outputDurationSlider = QSlider(orientation=Qt.Horizontal)
outputDurationLabel = QLabel('Output duration (in seconds): 2')
outputDurationSlider.setRange(1, 10)
outputDurationSlider.setValue(2)
outputDurationSlider.valueChanged.connect(lambda: outputDurationLabel.setText('Output duration (in seconds): ' + str(outputDurationSlider.value())))

# run granular synthesis
runButton = QPushButton('Run')
runButton.clicked.connect(run_granular)

# progress bar
progressBar = QProgressBar(orientation=Qt.Horizontal)
progressBar.setRange(0, 100)
progressBar.setValue(0)

# show layouts on the screen
layout = QVBoxLayout()
layout.addWidget(inputLabel)
layout.addWidget(openFileButton)
layout.addWidget(outputLabel)
layout.addWidget(setOutButton)
layout.addWidget(grainDurLabel)
layout.addWidget(grainDurSlider)
layout.addWidget(grainGenRateLabel)
layout.addWidget(grainGenRateSlider)
layout.addWidget(pitchLabel)
layout.addWidget(pitchSlider)
layout.addWidget(locationLabel)
layout.addWidget(locationSlider)
layout.addWidget(outputDurationLabel)
layout.addWidget(outputDurationSlider)
layout.addWidget(runButton)
layout.addWidget(progressBar)
window.setLayout(layout)
window.setLayout(layout)

window.show()
app.exec_()
