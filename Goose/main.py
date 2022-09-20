import digitalio
import board
import neopixel
import audioio
import busio
import adafruit_lis3dh
import time

# constants
NUM_PIXELS = 3  # NeoPixel pixels length (in pixels)
HONK = "Honk.wav"
TRIGGER_PIN = board.D9


# Enables the high power functions of the propwing
enable = digitalio.DigitalInOut(board.D10)
enable.direction = digitalio.Direction.OUTPUT
enable.value = True

# Speaker
audio = audioio.AudioOut(board.A0)

# trigger switch
switch = digitalio.DigitalInOut(TRIGGER_PIN)
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP


def honk():
    wave_file = open(HONK, "rb")
    wave = audioio.WaveFile(wave_file)
    audio.play(wave)
    while audio.playing:
        pass
        # time.sleep(0.2)
    # time.sleep(1)

# Main Loop
while True:
    if not switch.value:
        honk()