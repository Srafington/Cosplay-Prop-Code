# The MIT License (MIT)
#
# Copyright (c) 2017 Dan Halbert for Adafruit Industries
# Copyright (c) 2017 Kattni Rembor, Tony DiCola for Adafruit Industries
# Copyright (c) 2019 Jonathan Axford (Minor snippets of this)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
 
import array
import math
import time
 
import audiobusio
import board
import neopixel
 
# Exponential scaling factor.
# Should probably be in range -10 .. 10 to be reasonable.
CURVE = 2
SCALE_EXPONENT = math.pow(10, CURVE * -0.1)
 
PEAK_COLOR = (200, 0 , 200)
NUM_PIXELS = 10
 
# Number of samples to read at once.
NUM_SAMPLES = 160

#Light hold time in millis
MAX_TIME_BETWEEN_PEAKS = 500

#Play with this value to find a good spot to have the light triger on your voice
SENSITIVITY = 80
 
 
# Restrict value to be between floor and ceiling.
def constrain(value, floor, ceiling):
    return max(floor, min(value, ceiling))
 
 
# Scale input_value between output_min and output_max, exponentially.
def log_scale(input_value, input_min, input_max, output_min, output_max):
    normalized_input_value = (input_value - input_min) / \
                             (input_max - input_min)
    return output_min + \
        math.pow(normalized_input_value, SCALE_EXPONENT) \
        * (output_max - output_min)
 
 
# Remove DC bias before computing RMS.
def normalized_rms(values):
    minbuf = int(mean(values))
    samples_sum = sum(
        float(sample - minbuf) * (sample - minbuf)
        for sample in values
    )
 
    return math.sqrt(samples_sum / len(values))
 
 
def mean(values):
    return sum(values) / len(values)
 
 
def volume_color(volume):
    return 200, 0 , 200
 
 
# Main program
 
 
# Set up NeoPixels and turn them all off.
pixels = neopixel.NeoPixel(board.NEOPIXEL, NUM_PIXELS,
                           brightness=0.1, auto_write=False)
pixels.fill(0)
pixels.show()
 
mic = audiobusio.PDMIn(board.MICROPHONE_CLOCK, board.MICROPHONE_DATA,
                       sample_rate=16000, bit_depth=16)
 
# Record an initial sample to calibrate. Assume it's quiet when we start.
samples = array.array('H', [0] * NUM_SAMPLES)
mic.record(samples, len(samples))
# Set lowest level to expect, plus a little.
input_floor = normalized_rms(samples) + 10
# OR: used a fixed floor
# input_floor = 50
 
# You might want to print the input_floor to help adjust other values.
# print(input_floor)
 
# Corresponds to sensitivity, adjust with the SENSITIVITY constant
# Adjust this as you see fit.
input_ceiling = input_floor + 500
time_of_last_peak = 0
peak = 0
while True:
    mic.record(samples, len(samples))
    magnitude = normalized_rms(samples)
    # You might want to print this to see the values.
    # print(magnitude)
 
    # Compute scaled logarithmic reading in the range 0 to NUM_PIXELS
    c = log_scale(constrain(magnitude, input_floor, input_ceiling),
                  input_floor, input_ceiling, 0, NUM_PIXELS)
 
    # Light up pixels if we hit the sensitivity threshold, and hold them there for MAX_TIME_BETWEEN_PEAKS
    millis = int(round(time.time() * 1000))
    if c > input_ceiling/80 :
      pixels.fill(volume_color(0))
      time_of_last_peak = millis
    elif millis - time_of_last_peak > MAX_TIME_BETWEEN_PEAKS:
      pixels.fill(0)
    pixels.show()