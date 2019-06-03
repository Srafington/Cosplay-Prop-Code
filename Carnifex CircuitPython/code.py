# This is a revisit of the Carnifex hardware and code
# This is built around the Adafruit Feather M4 Express or the M0 Express
# It is supported by the Propmaker Wing
# All of this means that there is less supporting hardware, yet this prop is more capable
# With a minor edit to the model, you should be able to include a 3w 4ohm mini speaker
# You will no longer need a vibration switch, as we will use the wing's accelerometer
# You will no longer need the lipo backpack, as a charger is built into the feather
# The structure of this will act to protect the lipo cell (buy a long and narrow 400 mAh cell)
# For best results, mix any audio files down to mono

import digitalio
import board
import neopixel
import audioio
import busio
import adafruit_lis3dh
import time

# constants
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

# Enables the high power functions of the propwing
enable = digitalio.DigitalInOut(board.D10)
enable.direction = digitalio.Direction.OUTPUT
enable.value = True

# Speaker
audio = audioio.AudioOut(board.A0)

# Propwing's accelerometer, we'll use this to "reload" the gun by hitting it
# You can mimic the motion used in-game to trigger this
i2c = busio.I2C(board.SCL, board.SDA)
int1 = digitalio.DigitalInOut(board.D6)
accel = adafruit_lis3dh.LIS3DH_I2C(i2c, int1=int1)
accel.range = adafruit_lis3dh.RANGE_8_G
accel.set_tap(1, 100)

# trigger switch
switch = digitalio.DigitalInOut(TRIGGER_PIN)
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP

# Neopixels
pixels = neopixel.NeoPixel(board.D5, NUM_PIXELS, brightness=1)

shot_counter = 0

def fire():
    wave_file = open(WAV_FIRE, "rb")
    wave = audioio.WaveFile(wave_file)
    audio.play(wave)
    while audio.playing:
        pixels[1] = NEOPIX_COLOUR_BARREL
    pixels[1] = NEOPIX_OFF
    time.sleep(1)

def overheat():
    wave_file = open(WAV_OVERHEAT, "rb")
    wave = audioio.WaveFile(wave_file)
    audio.play(wave)
    while audio.playing:
        pass

def reload():
    wave_file = open(WAV_RELOAD, "rb")
    wave = audioio.WaveFile(wave_file)
    audio.play(wave)
    while audio.playing:
        pass
pixels[0] = NEOPIX_COLOUR_SIDES
pixels[2] = NEOPIX_COLOUR_SIDES
# Main Loop
while True:
    if not switch.value:
        if shot_counter < MAX_ROUNDS:
            pixels[0] = NEOPIX_COLOUR_SIDES
            pixels[2] = NEOPIX_COLOUR_SIDES
            shot_counter += 1
            fire()
            if shot_counter == MAX_ROUNDS:
                pixels[0] = NEOPIX_COLOUR_SIDES_OVERHEAT
                pixels[2] = NEOPIX_COLOUR_SIDES_OVERHEAT
        else:
            overheat()
    if accel.tapped and shot_counter > 0:
        reload()
        shot_counter = 0
        pixels[0] = NEOPIX_COLOUR_SIDES
        pixels[2] = NEOPIX_COLOUR_SIDES
    pixels.show()