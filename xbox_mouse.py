import inputs
import os
import pyautogui
import threading

DISPLAY = False
MOUSE_MULT = 1.5
SCROLL_MULT = 3

running = True
mouse_sensitivity = 0.001
scroll_sensitivity = 0.001
mouse_epsilon = 5
scroll_epsilon = 5
cache = {}

pyautogui.FAILSAFE = False
pyautogui.PAUSE = False


def move():
	if running:
	
		# Run 100 times per second
		threading.Timer(0.01, move).start()
		
		# Left Analog -> Update mouse
		abs_x = cache.get('ABS_X', 0)
		abs_y = cache.get('ABS_Y', 0)
		mouse_dx = int(abs_x * mouse_sensitivity)
		mouse_dy = int(-abs_y * mouse_sensitivity)
		if mouse_dx ** 2 + mouse_dy ** 2 > mouse_epsilon ** 2:
			pyautogui.moveRel(mouse_dx, mouse_dy)
			
		# Right Analog -> Scroll
		abs_ry = cache.get('ABS_RY', 0)
		scroll_dy = int(abs_ry * scroll_sensitivity)
		if abs(scroll_dy) > scroll_epsilon:
			pyautogui.vscroll(scroll_dy)
		
		
def listen():
	global running, mouse_sensitivity, scroll_sensitivity, mouse_epsilon, scroll_epsilon
	
	while running:
		for event in inputs.get_gamepad():
			if event.code != 'SYN_REPORT':
				cache[event.code] = event.state
				if DISPLAY:
					print(event.code, event.state)
				
				# If button was pressed (not released)
				if event.state in {-1, 1}:
					
					# A -> Left mouse click
					if event.code == 'BTN_SOUTH':
						res = pyautogui.click(button='left')
					
					# B -> Right mouse click
					if event.code == 'BTN_EAST':
						pyautogui.click(button='right')
						
					# D-Pad vertical -> mouse sensitivity
					if event.code == 'ABS_HAT0Y':
						mult = MOUSE_MULT ** -event.state
						mouse_sensitivity *= mult
						mouse_epsilon *= mult
					
					# D-Pad horizontal -> scroll sensitivity
					if event.code == 'ABS_HAT0X':
						mult = SCROLL_MULT ** event.state
						scroll_sensitivity *= mult
						scroll_epsilon *= mult
					
					# Select -> Open on screen keyboard
					# BUG: Unable to click on osk
					if event.code == 'BTN_SELECT':
						threading.Thread(target=os.system, args=['osk']).start()
					
					# Start -> Stop running
					if event.code == 'BTN_START':
						running = False			


def main():
	global running
	
	try:
		move()
		listen()
	except Exception as e:
		print(e)
		
		# Stop move thread
		running = False


if __name__ == '__main__':
	main()