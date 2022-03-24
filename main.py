import socket
import midi
import time
import threading
import os
kernel = "windows"
if "uname" in dir(os):
	kernel = os.uname()[4]
rpi = kernel == "armv7l"
if rpi:
	print("Running on a raspberry pi")
	from screen import ScreenController
else:
	print("Running desktop version")
	from desktop import ScreenController
import mpk
from PIL import Image

s = ScreenController()

program_selected = 1
volume = 127
reverb_size = 0
chorus = 0
last_changed = "Volume"
quiet_mode = False


MODE_CHOOSE_PROGRAM = 1
MODE_MAIN_MENU = 2
MODE_SETUP_MIDI = 3
MODE_MIDI_IN = 4
MODE_MIDI_OUT = 5

# called in UI thread
def update_ui():
	mode = MODE_CHOOSE_PROGRAM
	global program_selected, last_changed, volume, reverb_size, chorus, quiet_mode

	previous_values = {
		"reverb_size": reverb_size
	}
	# load image
	s.load_image("keys.png")
	image_names = ["keyboard", 
		"chromatic_percussion", 
		"organ", 
		"guitar", 
		"bass", 
		"strings", 
		"ensemble", 
		"brass",
		"reed",
		"pipe",
		"synth_lead",
		"synth_pad",
		"synth_effects",
		"ethnic",
		"percussive",
		"sound_effects"]
	images = []
	for name in image_names:
		print("Loading " + name)
		images.append(Image.open("images/" + name + ".png"))
	
	programs = []

	# load list of program names
	with open("midi_programs.txt") as f:
		contents = f.read().split("\n")
		for line in contents:
			programs.append(line)

	t = 0
	option = 0
	while True:
		pipe = mi.ui_pipe
		buttons = s.get_buttons()

		if mode == MODE_CHOOSE_PROGRAM:
			group = program_selected // 8
			s.image = images[group % len(images)]
			d = s.get_drawing()
			d.rectangle((0,0, 128, 20), fill=(255,255,255,255))

			#control property slider
			d.rectangle((0,115,40,125), fill=(255,255,255,255))
			s.print(last_changed, fill=(0,0,0,255), update=False, pos=(1, 115))
			d.rectangle((0,125,128,128), fill=(0,0,0,255))
			if last_changed == "Volume":
				d.rectangle((0,125,volume+1,128), fill=(255,0,0,255))
			if last_changed == "Chorus":
				d.rectangle((0,125,chorus+1,128), fill=(0,255,0,255))
			if last_changed == "Reverb":
				d.rectangle((0,125,reverb_size+1,128), fill=(0,0,255,255))
			
			
			# program
			s.print(str(program_selected), fill=(255,0,0,255), pos=(60,0),update=False)
			s.print(programs[program_selected], pos=(0,10), fill=(0,0,0,255),update=False)
			s.update()		
			if "1" in buttons:
				program_selected = (program_selected - 1) % 128
				mi.change_program(program_selected)
			if "3" in buttons:
				program_selected = (program_selected + 1) % 128
				mi.change_program(program_selected)

			if "left" in buttons:
				mode = MODE_MAIN_MENU

		elif mode == MODE_MAIN_MENU:
			options = ["Change sound", "MIDI devices", "Shutdown"]
			d = s.get_drawing(True)
			d.rectangle((0,0,128,128), fill=(255,255,255,255))
			s.print("MidiPi Main menu", fill=(0,0,255,255), pos=(0,0), update=False)

			y = 20
			for i in range(len(options)):
				if i == option:
					d.rectangle((0,y,128,y+20), fill=(255,0,0,255))
				s.print(options[i], fill=(0,0,0,255), pos=(0,y), update=False)
				y+=20
			s.update()

			if "down" in buttons:
				option += 1
				if option > len(options) - 1:
					option = 0
			
			if "up" in buttons:
				option -= 1
				if option < 0:
					option = len(options) - 1

			if "middle" in buttons:
				# Change sound
				if option == 0:
					mode = MODE_CHOOSE_PROGRAM
				elif option == 1:
					mode = MODE_SETUP_MIDI
					option = 0
				elif option == 2:
					if kernel == "windows":
						exit()
					else:
						os.system("sudo shutdown -h now")
				
			if "left" in buttons:
				mode = MODE_CHOOSE_PROGRAM
		
		elif mode == MODE_SETUP_MIDI:
			options = ["MIDI input devices", "MIDI output devices", "Rescan for devices"]
			d = s.get_drawing(True)
			d.rectangle((0,0,128,128), fill=(255,255,255,255))
			s.print("MIDI Setup", fill=(0,0,255,255), pos=(0,0), update=False)

			y = 20
			for i in range(len(options)):
				if i == option:
					d.rectangle((0,y,128,y+20), fill=(255,0,0,255))
				s.print(options[i], fill=(0,0,0,255), pos=(0,y), update=False)
				y+=20
			s.update()

			if "down" in buttons:
				option += 1
				if option > len(options) - 1:
					option = 0
			
			if "up" in buttons:
				option -= 1
				if option < 0:
					option = len(options) - 1

			if "middle" in buttons:
				# MIDI In
				if option == 0:
					option = 0
					mode = MODE_MIDI_IN
				elif option == 1:
					option = 0
					mode = MODE_MIDI_OUT
				elif option == 2:
					option = 0
					mi.stop()
					mi.scan()
				
			if "left" in buttons:
				mode = MODE_MAIN_MENU

		elif mode == MODE_MIDI_IN:
			options = mi.available_inputs
			d = s.get_drawing(True)
			d.rectangle((0,0,128,128), fill=(255,255,255,255))
			s.print("MIDI Input devces", fill=(0,0,255,255), pos=(0,0), update=False)

			y = 20
			connected = []
			for i in range(len(options)):
				c = False
				for p in mi.connected_inputs:
					if p == options[i]:
						c = True
				connected.append(c)
				if i == option:
					d.rectangle((0,y,128,y+20), fill=(255,0,0,255))
				m = "[ ] "
				if connected[i]:
					m = "[X] "
				s.print(m + options[i], fill=(0,0,0,255), pos=(0,y), update=False)
				y+=20
			s.update()

			if "down" in buttons:
				option += 1
				if option > len(options) - 1:
					option = 0
			
			if "up" in buttons:
				option -= 1
				if option < 0:
					option = len(options) - 1

			if "middle" in buttons:
				if connected[option]:
					mi.disconnect_input(options[option])
				else:
					mi.connect_input(options[option])
				mi.reconnect()
				
			if "left" in buttons:
				mode = MODE_SETUP_MIDI
		
		elif mode == MODE_MIDI_OUT:
			options = mi.available_outputs
			d = s.get_drawing(True)
			d.rectangle((0,0,128,128), fill=(255,255,255,255))
			s.print("MIDI Output devces", fill=(0,0,255,255), pos=(0,0), update=False)

			y = 20
			connected = []
			for i in range(len(options)):
				c = False
				for p in mi.connected_outputs:
					if p == options[i]:
						c = True
				connected.append(c)
				if i == option:
					d.rectangle((0,y,128,y+20), fill=(255,0,0,255))
				m = "[ ] "
				if connected[i]:
					m = "[X] "
				s.print(m + options[i], fill=(0,0,0,255), pos=(0,y), update=False)
				y+=20
			s.update()

			if "down" in buttons:
				option += 1
				if option > len(options) - 1:
					option = 0
			
			if "up" in buttons:
				option -= 1
				if option < 0:
					option = len(options) - 1

			if "middle" in buttons:
				if connected[option]:
					mi.disconnect_output(options[option])
				else:
					mi.connect_output(options[option])
				mi.reconnect()
				
			if "left" in buttons:
				mode = MODE_SETUP_MIDI
		midi_msg_count = 0
		while pipe.poll(.1):
			midi_msg_count += 1
			if midi_msg_count > 10:
				break
			msg = pipe.recv()
			handle_midi(msg)
		
def handle_midi(msg):
	global program_selected, last_changed, volume, reverb_size, chorus, quiet_mode
	if msg.type=="note_on":
		if not quiet_mode:
			print("Note on:", msg.note, msg.channel, msg.velocity)
	elif msg.type=="note_off":
		if not quiet_mode:
			print("Note off:",msg.note, msg.channel, msg.velocity)
	elif msg.type=="control_change":
		if not quiet_mode:
			print("Control change: ", msg)
		if msg.control==3:
			program_selected = msg.value
			
		# reverb room size
		if msg.control==91:
			reverb_size = msg.value
			last_changed = "Reverb"

		# chorus size
		if msg.control==93:
			chorus = msg.value
			last_changed = "Chorus"		

		# volume
		if msg.control==7:
			volume = msg.value
			last_changed = "Volume"
	else:
		if not quiet_mode:
			print(msg)

if __name__ == "__main__":
	# connect midi devices
	m = mpk.Akai_MPK_Mini()
	m.send_RAM()
	
	mi = midi.MidiEngine(quiet_mode=False)

	
	#show_all()

	mi.connect_input("MPK", method=midi.MATCH_REGEX)
	mi.connect_output("FLUID", method=midi.MATCH_REGEX)
	mi.connect_output("TD-17", method=midi.MATCH_REGEX)

	#mi.connect_input(0, method=midi.MATCH_INDEX)
	#mi.connect_output(0, method=midi.MATCH_INDEX)
	mi.listen_all()
	print(mi.connected_outputs, mi.connected_inputs)
	#midi_thread = threading.Thread(target=update_midi)
	#midi_thread.start()

	update_ui()

