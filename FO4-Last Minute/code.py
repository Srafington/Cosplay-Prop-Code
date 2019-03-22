import digitalio
import board
import neopixel
import audioio
from exixe import Exixe 
import time
import busio
import pulseio


NUM_PIXELS = 4  # NeoPixel strip length (in pixels)
WAV_FIRE = "fire.wav"
WAV_CHARGE = "charge.wav"
WAV_CHARGED = "steady.wav"
TRIGGER_PIN = board.D9
NEOPIX_COLOUR = [45,223,255]

enable = digitalio.DigitalInOut(board.D10)
enable.direction = digitalio.Direction.OUTPUT
enable.value = True

# Speaker
audio = audioio.AudioOut(board.A0)

# Nixies
cs1 = board.D4
cs2 = board.A5
mosi = board.MOSI
sck = board.SCK
spi = busio.SPI(sck, mosi)
Nixie2 = Exixe(cs1, spi, False, 0)
Nixie1 = Exixe(cs2, spi, False, 0)
Nixie1.set_led(0,0,0)
Nixie2.set_led(0,0,0) 

# High powered non addressable LED for muzzle flash
red = pulseio.PWMOut(board.D11, duty_cycle=0, frequency=20000)
green = pulseio.PWMOut(board.D12, duty_cycle=0, frequency=20000)
blue = pulseio.PWMOut(board.D13, duty_cycle=0, frequency=20000)

# trigger switch
switch = digitalio.DigitalInOut(TRIGGER_PIN)
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP

# Neopixels
strip = neopixel.NeoPixel(board.D5, NUM_PIXELS, brightness=1)

def fire():
    wave_file = open(WAV_FIRE, "rb")
    wave = audioio.WaveFile(wave_file)
    fired = False
    Nixie2.set_digit(0)
    Nixie1.set_digit(0)
    strip.fill((0,0,0))
    audio.play(wave)
    while audio.playing:
        if not fired:
            for i in range(-100,1):
                red.duty_cycle = int(i * -65535/100)
                green.duty_cycle = int(i * -65535/100)
                blue.duty_cycle = int(i * -65535/100)
                time.sleep(0.002)
                if i == 0:
                    fired = True

def charge():
    charged = False
    wave_charge_file = open(WAV_CHARGE, "rb")
    wave_charge = audioio.WaveFile(wave_charge_file)
    audio.play(wave_charge)
    while audio.playing:
        if not charged:
            for i in range(0,100):
                r = int(i/99 * NEOPIX_COLOUR[0])
                g = int(i/99 * NEOPIX_COLOUR[1])
                b = int(i/99 * NEOPIX_COLOUR[2])
                strip.fill((r,g,b))
                Nixie2.set_digit(i%10)
                Nixie1.set_digit(int(i/10))
                    
                time.sleep(0.005)
                if i == 99:
                    charged = True
                if switch.value:
                    break
        if switch.value:
            audio.stop()
            break
    wave_charged_file = open(WAV_CHARGED, "rb")
    wave_charged = audioio.WaveFile(wave_charged_file)
    while not switch.value:
        audio.play(wave_charged)
        while audio.playing:
            strip.fill(tuple(NEOPIX_COLOUR))
            if switch.value:
                audio.stop()
                break
    fire()


# Main Loop 
while True:
    Nixie1.set_led(0,0,0)
    Nixie2.set_led(0,0,0) 
    if not switch.value: 
        charge()
             