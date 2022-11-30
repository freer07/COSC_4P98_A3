# Alexander Freer
# 6452551
# Granular Synthesis Engine

# To Run: python 'inputFile.txt' 'outputFile.txt' sampleRate grainLength(ms) grainDensity(grains/sec) pitch location(% of original audio available) duration(sec)
# Ex. python .\GranularSynth.py 'SampleAudioConverted.txt' 'test.txt' 44100 100 200 -12 .8 2
import sys
import random
from tqdm import tqdm

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

    for j in range(grainSize):
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


inFileName = str(sys.argv[1])
outFileName = str(sys.argv[2])
sampleRate = int(sys.argv[3])
grainDur = int(sys.argv[4]) #should be between 1ms-100ms
grainGenRate = float(sys.argv[5]) # grains/second
pitch = int(sys.argv[6])
location = float(sys.argv[7]) #min and max locations from center, from which grains are generated (.8 means 80% thus, no grains in first 10% and final 10% of audio)
outputDuration = int(sys.argv[8]) #seconds

origFile = open(inFileName, "r")
newFile = open(outFileName, "w")

samples = origFile.readlines()
samples = list(map(lambda n: float(n), samples))

p = 1 - location
start = int(len(samples)*(p/2))
end = int(len(samples) - start)

#trim sample list to get start and end index
samples = samples[start:end]


outputBuffer = [0] * (outputDuration * sampleRate) #initialize output buffer with 0's

# pad the input samples with 0's if output is longer
if len(outputBuffer) > len(samples) :
    samples += [0] * (len(outputBuffer) - len(samples))

probability = grainGenRate / sampleRate
grainSize = int((grainDur / 1000) * sampleRate)

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
        
for sample in outputBuffer:
    newFile.write(str(sample) + "\n")

origFile.close()
newFile.close()