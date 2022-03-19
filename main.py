import socket
import mido
import time
import threading
import os
kernel = "windows"
if "uname" in dir(os):
	kernel = os.uname()
rpi = "aarch64" in kernel
if rpi:
	print("Running on a raspberry pi")
	from screen import ScreenController
else:
	print("Running desktop version")
	from desktop import ScreenController
import mpk
from PIL import Image

s = ScreenController()

inputs = mido.get_input_names()
outputs = mido.get_output_names()
ports_in = []
ports_out = []
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
	global program_selected
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
				update_program()
			if "3" in buttons:
				program_selected = (program_selected + 1) % 128
				update_program()

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
					os.system("sudo shutdown -h now")
					exit()
				
			if "left" in buttons:
				mode = MODE_CHOOSE_PROGRAM
		
		elif mode == MODE_SETUP_MIDI:
			options = ["MIDI input devices", "MIDI output devices"]
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
				
			if "left" in buttons:
				mode = MODE_MAIN_MENU

		elif mode == MODE_MIDI_IN:
			options = inputs
			d = s.get_drawing(True)
			d.rectangle((0,0,128,128), fill=(255,255,255,255))
			s.print("MIDI Input devces", fill=(0,0,255,255), pos=(0,0), update=False)

			y = 20
			connected = []
			for i in range(len(options)):
				c = False
				for p in ports_in:
					if p.name == options[i]:
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
					disconnect_input(option)
				else:
					connect_input(option)
				reconnect_midi()
				
			if "left" in buttons:
				mode = MODE_SETUP_MIDI
		
		elif mode == MODE_MIDI_OUT:
			options = outputs
			d = s.get_drawing(True)
			d.rectangle((0,0,128,128), fill=(255,255,255,255))
			s.print("MIDI Output devces", fill=(0,0,255,255), pos=(0,0), update=False)

			y = 20
			connected = []
			for i in range(len(options)):
				c = False
				for p in ports_out:
					if p.name == options[i]:
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
					disconnect_output(option)
				else:
					connect_output(option)
				reconnect_midi()
				
			if "left" in buttons:
				mode = MODE_SETUP_MIDI

		time.sleep(.1)
		

def update_program():
	print("Program changed to", program_selected)
	m = mido.Message("program_change", program=program_selected, channel=0)
	for p in  ports_out:
		p.send(m)


def show_all():
	print("Inputs:")
	for i in range(len(inputs)):
		print("*", i, inputs[i])
	print("Outputs:")
	for i in range(len(outputs)):
		print("*", i, outputs[i])

def connect_all():
	for midi_input in inputs:
		print("Connecting to input" + midi_input)
		port = mido.open_input(midi_input)
		ports_in.append(port)
	for midi_output in outputs:
		print("Connecting to output" + midi_output)
		port = mido.open_output(midi_output)
		ports_out.append(port)

def connect_input(index = -1, match=""):
		# search for device matching description
	if len(match) > 0:
		for i in range(len(inputs)):
			if match in inputs[i]:
				index = i
				print("Found input device:", inputs[i])
				break

	if index > -1:
		midi_input = inputs[index]
		print("Connecting to " + midi_input)
		port = mido.open_input(midi_input)
		ports_in.append(port)

def connect_output(index=-1, match=""):
	# search for device matching description
	if len(match) > 0:
		for i in range(len(outputs)):
			if match in outputs[i]:
				index = i
				print("Found output device:", outputs[i])
				break
	if index > -1:
		midi_output = outputs[index]
		print("Connecting to output " + midi_output)
		port = mido.open_output(midi_output)
		ports_out.append(port)

def disconnect_output(index=-1, match=""):
	# search for device matching description
	if len(match) > 0:
		for i in range(len(outputs)):
			if match in outputs[i]:
				index = i
				print("Found output device:", outputs[i])
				break
	if index > -1:
		midi_output = outputs[index]
		for o in ports_out:
			if o.name == midi_output:
				o.close()
				print("Disconnecting to output " + midi_output)
				ports_out.remove(o)
				break

def disconnect_input(index=-1, match=""):
	# search for device matching description
	if len(match) > 0:
		for i in range(len(inputs)):
			if match in inputs[i]:
				index = i
				print("Found input device:", outputs[i])
				break
	if index > -1:
		midi_input = inputs[index]
		for o in ports_in:
			if o.name == midi_input:
				o.close()
				print("Disconnecting from input " + midi_input)
				ports_in.remove(o)
				break

def update_midi():
	print("Connected to: ", ports_in, ports_out)
	for port, msg in mido.ports.multi_receive(ports_in, yield_ports=True):
		
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
				m = mido.Message("program_change", program=msg.value, channel=msg.channel)
				program_selected = msg.value
				for p in  ports_out:
					p.send(m)
			
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
		for p in ports_out:
			p.send(msg)
		#s.show_status()

def reconnect_midi():
	global midi_thread
	midi_thread.terminate()
	print("Closing midi devices and restarting")
	midi_thread = threading.Thread(target=update_midi)
	midi_thread.start()


if __name__ == "__main__":
	# connect midi devices
	m = mpk.Akai_MPK_Mini()
	m.send_RAM()
	show_all()
	connect_input(match="MPK")
	connect_output(match="FLUID")
	connect_output(match="TD-17")
	midi_thread = threading.Thread(target=update_midi)
	midi_thread.start()

	update_ui()

