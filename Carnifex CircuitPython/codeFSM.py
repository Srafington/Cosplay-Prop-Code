# This is a revisit of the Carnifex hardware and code, now written as a finite state machine
# This is built around the Adafruit Feather M4 Express or the M0 Express
# It is supported by the Propmaker Wing
# All of this means that there is less supporting hardware, yet this prop is more capable
# With a minor edit to the model, you should be able to include a 3w 4ohm mini speaker
# You will no longer need a vibration trigger, as we will use the wing's accelerometer
# You will no longer need the lipo backpack, as a charger is built into the feather
# The structure of this will act to protect the lipo cell (buy a long and narrow 400 mAh cell)
# For best results, mix any audio files down to mono
# Runs on: CircuitPython 6

import digitalio
import board
import neopixel
import audioio
import audiocore
import busio
import adafruit_lis3dh
import time


############ SETUP ############
# Constants #
# Enums are a bit different in Python, and the board I'm using doesn't include the enum library anyway.
# If we had more states, it would be worthwhile getting it, and using the enum object class
OFF = 1 
READY = 2,
OVERHEAT = 3
NUM_PIXELS = 3  # NeoPixel pixels length (in pixels)
WAV_FIRE = "fire.wav"
WAV_OVERHEAT = "overheat.wav"
WAV_RELOAD = "reload.wav"
TRIGGER_PIN = board.D9
NEOPIX_OFF = (0, 0, 0)
NEOPIX_COLOUR_SIDES = (28, 255, 236)
NEOPIX_COLOUR_SIDES_OVERHEAT = (255, 0, 0)
# you may need to adjust the following value
# The through-hole pixel I used for the barrel uses a GRB model
NEOPIX_COLOUR_BARREL = (83, 255, 15)
# Carnifex has 5 rounds per thermal clip
MAX_ROUNDS = 5
RAISE_THRESHOLD = 5
LOWER_THRESHOLD = 7

# Device setup #

# Preps the power management pin
enable = digitalio.DigitalInOut(board.D10)
enable.direction = digitalio.Direction.OUTPUT

# Speaker
audio = audioio.AudioOut(board.A0)

# Propwing's accelerometer, we'll use this to "reload" the gun by hitting it
# You can mimic the motion used in-game to trigger this
i2c = busio.I2C(board.SCL, board.SDA)
int1 = digitalio.DigitalInOut(board.D6)
accel = adafruit_lis3dh.LIS3DH_I2C(i2c, int1=int1)
accel.range = adafruit_lis3dh.RANGE_4_G
accel.set_tap(1, 100)

# trigger switch
trigger = digitalio.DigitalInOut(TRIGGER_PIN)
trigger.direction = digitalio.Direction.INPUT
trigger.pull = digitalio.Pull.UP

# Neopixels
pixels = neopixel.NeoPixel(board.D5, NUM_PIXELS, brightness=1)

# Global Variables
shotCounter = 0
currentState = OFF
offStateFirstRun = True
readyStateFirstRun = True
overheatFirstRun = True

############ FUNCTIONS ############ 
#  
# state machine runner
def runStateMachine():
    stateMachine = stateMachineDictionary.get(currentState, "Invalid state")
    return stateMachine()

# Helper for managing measurements from the accelerometer 
def isPropRaised(threshold):
    x, y, z = accel.acceleration
    #Z and X axes align with the barrel and grip, while the Y axis is orthogonal, and is thus useful as an pitch indicator
    if y < threshold:
        return True
    return False

# Manages the OFF state, can switch to READY if the prop is raised, an ammo is available
# Will move to overheat if ammo is expended and raised
def runOffState():
    global offStateFirstRun
    global currentState
    global shotCounter
    if offStateFirstRun:
        #Smooth out transitions to prevent state jumping if the threashold is crossed slowly
        time.sleep(.5)
        offStateFirstRun = False
        # the propwing has an enable pin that can be used to cut power to all "high power" 
        # features, including the amplifier and neopixels, saving battery
        enable.value = False
        pixels.show()
    isRaised = isPropRaised(RAISE_THRESHOLD)
    if isRaised and shotCounter < MAX_ROUNDS:
        offStateFirstRun = True
        currentState = READY
        print("moving to active state")
    elif isRaised and shotCounter >= MAX_ROUNDS:
        offStateFirstRun = True
        currentState = OVERHEAT
        print("moving to overheat state")

# Manages the READY state, can switch to OFF if the prop is lowered, or OVERHEAT if
# the shot counter maxes out
def runReadyState():
    global readyStateFirstRun
    global currentState
    global shotCounter
    global trigger
    if readyStateFirstRun:
        #Smooth out transitions to prevent state jumping if the threashold is crossed slowly
        time.sleep(.5)
        readyStateFirstRun = False
        enable.value = True
        pixels[0] = NEOPIX_COLOUR_SIDES
        pixels[1] = NEOPIX_OFF
        pixels[2] = NEOPIX_COLOUR_SIDES
        pixels.show()
    
    if not isPropRaised(LOWER_THRESHOLD):
        readyStateFirstRun = True
        currentState = OFF
        print("moving to off state")
    elif shotCounter >= MAX_ROUNDS:
        readyStateFirstRun = True
        currentState = OVERHEAT
        print("moving to overheat state")
    elif not trigger.value:
        fire()
    elif accel.tapped and shotCounter > 0:
        reload()
        

# Manages the overheat state, can switch to the READY state if the prop is struck (triggering the accelerometer)
# Will move to the OFF state if the prop is lowered 
def runOverheatState():
    global overheatFirstRun
    global currentState
    global shotCounter
    global trigger
    if overheatFirstRun:
        overheatFirstRun = False
        enable.value = True
        pixels[0] = NEOPIX_COLOUR_SIDES_OVERHEAT
        pixels[1] = NEOPIX_OFF
        pixels[2] = NEOPIX_COLOUR_SIDES_OVERHEAT
        pixels.show()
    
    if accel.tapped:
        reload()
        overheatFirstRun = True
        currentState = READY
        print("moving to active state")
    if not isPropRaised(LOWER_THRESHOLD):
        overheatFirstRun = True
        currentState = OFF
        print("moving to off state")
    elif not trigger.value:
        fireOverheat()


# Function that handles the behaviour if the trigger is pulled while READY is active
def fire():
    global shotCounter
    shotCounter += 1
    wave_file = open(WAV_FIRE, "rb")
    wave = audiocore.WaveFile(wave_file)
    audio.play(wave)
    while audio.playing:
        pixels[1] = NEOPIX_COLOUR_BARREL
    pixels[1] = NEOPIX_OFF
    time.sleep(1)

# Function that handles the behaviour if the trigger is pulled while OVERHEAT is active
def fireOverheat():
    wave_file = open(WAV_OVERHEAT, "rb")
    wave = audiocore.WaveFile(wave_file)
    audio.play(wave)
    while audio.playing:
        pass
    wave_file.close()

# Function that handles the "reload" behaviour (sound, shotcounter)
def reload():
    global shotCounter
    shotCounter = 0
    wave_file = open(WAV_RELOAD, "rb")
    wave = audiocore.WaveFile(wave_file)
    audio.play(wave)
    while audio.playing:
        pass

############ STATE MACHINE DEFINITION ############ 
# Needs to go after the declaration of the functions it refreences
# This dictionary get used like a switch
stateMachineDictionary = {
        OFF: runOffState,
        READY: runReadyState,
        OVERHEAT: runOverheatState 
    }


############ MAIN LOOP ############ 
while True:
    runStateMachine()
