#!/usr/bin/python3

#################################################################################
#
# MouseImp-like scrolling by dragging the mouse with the right button depressed.
# For Linux only.
#
# Features:
# Vertical scroll: RBtn + Y-drag
# Horizontal scroll: LeftShift + RBtn +  X-drag
#
# Copyright (c) 2024 PPRRPRR (J.VV.)
#
# CREDITS: MouseImp is the original great work by Nezhelsky Oskar et al.
# https://github.com/axxie/MouseImp
#
# REF: Input event codes:
# https://www.kernel.org/doc/html/latest/input/event-codes.html
# https://github.com/torvalds/linux/blob/master/include/uapi/linux/input.h
#
#################################################################################

from evdev import InputDevice, UInput, ecodes as ec
from threading import Thread
from time import time, sleep
import queue


# the mouse (may or may not be event 4); run /usr/bin/evtest to identify yours
input_mouse = InputDevice('/dev/input/event4')
output_mouse = UInput.from_device(input_mouse, name='Drag-scroll like MouseImp!')

# for modifying the behaviours with certain keys (e.g. KEY_LEFTSHIFT)
input_keybd = InputDevice('/dev/input/event5')

# thread-safe FIFO
deferred_ev = queue.Queue()
#deferred_ev = []

btn_side_depressed = 0
btn_extra_depressed = 0

#----------------------------------------------------
# (optional; comment out these lines if undesirable)
# timeout (in seconds) for a mouse button-depressed event to be regarded a 'single-click' if no subsequent mouse event follows shortly after
def single_click_timeout():
	global deferred_ev, output_mouse, btn_side_depressed, btn_extra_depressed
	hscroll_speed = 3
	threshold = 0.213

	while (True):
		now = time()
		# a mouse button-depressed action is actually comprised of a group of three events: EV_MSC, EV_KEY, EV_SYN
		# their timestamps are always identical (or almost identical), so we only need to check the timestamp of the latest of the three
		if 3 == deferred_ev.qsize():
			t = now - deferred_ev.queue[2].timestamp()
#			print(t)
			if (t > threshold): emit_all_deferred()

		elif btn_side_depressed:
			output_mouse.write(ec.EV_REL, ec.REL_HWHEEL, -hscroll_speed)
			output_mouse.write(ec.EV_REL, ec.REL_HWHEEL_HI_RES, -120 * hscroll_speed)
			output_mouse.syn()

		elif btn_extra_depressed:
			output_mouse.write(ec.EV_REL, ec.REL_HWHEEL, hscroll_speed)
			output_mouse.write(ec.EV_REL, ec.REL_HWHEEL_HI_RES, 120 * hscroll_speed)
			output_mouse.syn()

		sleep(threshold / 4)
Thread(target=single_click_timeout).start()

#----------------------------------------------------
def emit_all_deferred():
	global deferred_ev, output_mouse
	while not deferred_ev.empty(): output_mouse.write_event( deferred_ev.get() )

#----------------------------------------------------
def clear_all_deferred():
	global deferred_ev
	with deferred_ev.mutex: deferred_ev.queue.clear()

#----------------------------------------------------
# we will handle all mouse events exclusively from now on
input_mouse.grab()

rb_depressed = False

for event in input_mouse.read_loop():
#	for att in dir(event): print (att, getattr(event,att))

	# pressing a mouse button always triggers two events: MSC_SCAN BTN_RIGHT (or BTN_LEFT)
	if (ec.EV_MSC == event.type) and (ec.MSC_SCAN == event.code):
		# defer this event
#		deferred_ev.append(event)
		deferred_ev.put(event)
		continue

	elif (ec.EV_KEY == event.type) and (ec.BTN_RIGHT == event.code):
		# defer the right button event, regardless of whether it is depressed or released
#		deferred_ev.append(event)
		deferred_ev.put(event)

		rb_depressed = event.value

		# button is depressed --> come back to decide what to do later
		if rb_depressed:
#			print('>>> RB DN --> waiting for drag pattern')
			continue
		else:
#			print('>>> RB UP --> non drag, releasing all the deferred', len(deferred_ev), deferred_ev)
#			print('EV_MSC', ec.EV_MSC, 'MSC_SCAN', ec.MSC_SCAN, 'EV_SYN', ec.EV_SYN, 'EV_KEY', ec.EV_KEY, 'BTN_RIGHT', ec.BTN_RIGHT, 'EV_REL', ec.EV_REL)

			# button is released --> process all the deferred events (which also include the current one)
#			while deferred_ev: output_mouse.write_event( deferred_ev.pop(0) )
			emit_all_deferred()
			continue

#	if ec.EV_REL == event.type and ec.REL_WHEEL == event.code and key in kb.active_keys():

	# having deferred events implies that the mouse button is currently depressed
	elif rb_depressed and (ec.EV_REL == event.type):
		# suppress the original mouse button events, if any
#		deferred_ev.clear()
		clear_all_deferred()

		# perform vertical scrolling
		if event.code == ec.REL_Y:
#			print('>>> V-SCROLL')
			output_mouse.write(ec.EV_REL, ec.REL_WHEEL, -event.value)
			output_mouse.write(ec.EV_REL, ec.REL_WHEEL_HI_RES, -event.value * 120)
			# optionally, we can also allow the cursor to move
#			output_mouse.write(ec.EV_REL, ec.REL_Y, event.value)
			output_mouse.syn()
			continue

		# perform horizontal scrolling, with LEFTSHIFT key down
		elif event.code==ec.REL_X and (ec.KEY_LEFTSHIFT in input_keybd.active_keys()):
#			print('>>> H-SCROLL')
			output_mouse.write(ec.EV_REL, ec.REL_HWHEEL, event.value)
			output_mouse.write(ec.EV_REL, ec.REL_HWHEEL_HI_RES, event.value * 120)
			# optionally, we can also allow the cursor to move
#			output_mouse.write(ec.EV_REL, ec.REL_X, event.value)
			output_mouse.syn()
			continue

	elif (ec.EV_SYN == event.type):
#		if deferred_ev: deferred_ev.append(event)
		if not deferred_ev.empty(): deferred_ev.put(event)
		if rb_depressed: continue

	# wheel push left
	elif (ec.EV_KEY == event.type) and (ec.BTN_SIDE == event.code):
		btn_side_depressed = event.value
		continue

	# wheel push right
	elif (ec.EV_KEY == event.type) and (ec.BTN_EXTRA == event.code):
		btn_extra_depressed = event.value
		continue

	# no scroll intention --> execute all the deferred events, if any, plus the current one
#	print('>>> OTHER:', 'EV_SYN' if event.type == ec.EV_SYN else event.type)
#	deferred_ev.append(event)
#	while deferred_ev: output_mouse.write_event( deferred_ev.pop(0) )
	deferred_ev.put(event)
	emit_all_deferred()


# optional; when we exit this will be done automatically anyway
input_mouse.ungrab()
