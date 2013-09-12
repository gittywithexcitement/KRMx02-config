#!/usr/bin/python

# First zero the Z axis offset in G54, so that G54 matches machine coordinates (G53)
# G10 L2 P1 Z0

# Now move down towards the probe. Don't go any lower than the probe height (about 2.255), because if we go lower than that, we know that we've missed the probe. Do this at a relatively fast speed.
# G38.2 Z2.255 F16 G90

# Back off a little bit
# G91 G1 F50 Z0.01
# repeat at a slower speed to get a more accurate reading
# G90 G38.2 Z2.240 F1

# Now back off so that operator can remove the probe
# G0 Z0.5 G91
# TODO does this leave us in incremental mode? That would be bad.

# For all of these commands, we know to execute the next one once machine.in-position is true

# Inputs: start, in-position
# Outputs: 5 unique mdi commands

import hal, time

h = hal.component("z-probe")
h.newpin("z-touch-off", hal.HAL_BIT, hal.HAL_IN)
h.newpin("in-position", hal.HAL_BIT, hal.HAL_IN)
h.newpin("mdi-g54z0", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("mdi-g38fast", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("mdi-backoff-tiny", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("mdi-g38slow", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("mdi-backoff-final", hal.HAL_BIT, hal.HAL_OUT)
h.ready()

MDI_DURATION=1
# MDI_DURATION=0.001
SHORT_SLEEP=0.01

# current values
cv = {}

def init():
	h['mdi-g54z0'] = False
	h['mdi-g38fast'] = False
	h['mdi-backoff-tiny'] = False
	h['mdi-g38slow'] = False
	h['mdi-backoff-final'] = False

	# set these to false for good measure
	h['in-position'] = False
	h['z-touch-off'] = False

def setFor(signal, value, sleepTime):
	old = signal
	signal = value
	print(signal)
	print(value)
	time.sleep(sleepTime)
	signal = old

def waitForBegin():
	while not (h['z-touch-off'] and h['in-position']):
		time.sleep(SHORT_SLEEP)
	setFor(h['mdi-g54z0'], True, MDI_DURATION)
	setFor(h['mdi-g38fast'], True, MDI_DURATION)

def waitForFirstContact():
	while not (h['in-position']):
		time.sleep(SHORT_SLEEP)
	setFor(h['mdi-backoff-tiny'], True, MDI_DURATION)
	while not (h['in-position']):
		time.sleep(SHORT_SLEEP)
	setFor(h['mdi-g38slow'], True, MDI_DURATION)

def waitForSecondContact():
	while not (h['in-position']):
		time.sleep(SHORT_SLEEP)
	setFor(h['mdi-backoff-final'], True, MDI_DURATION)

try:
	init()
	while True:
		waitForBegin()
		print('tick')
		waitForFirstContact()
		print('tock')
		waitForSecondContact()
		print('tuck')
except KeyboardInterrupt:
    raise SystemExit
