import socket
import mido
import time
import threading
import os
kernel = os.uname()
rpi = "Raspberry" in kernel
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

# called in UI thread
def update_ui():
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
	while True:
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


		buttons = s.get_buttons()
		if "middle" in buttons:
			os.system("sudo shutdown -h now")

		if "1" in buttons:
			program_selected = (program_selected - 1) % 128
			update_program()
		if "3" in buttons:
			program_selected = (program_selected + 1) % 128
			update_program()

		if len(buttons) > 0:
			print(buttons)

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

def connect_input(index = 0, match=""):
	# search for device matching description
	if len(match) > 0:
		for i in range(len(inputs)):
			if match in inputs[i]:
				index = i
				print("Found input device:", inputs[i])
				break

	midi_input = inputs[index]
	print("Connecting to " + midi_input)
	port = mido.open_input(midi_input)
	ports_in.append(port)

def connect_output(index=0, match=""):
	# search for device matching description
	if len(match) > 0:
		for i in range(len(outputs)):
			if match in outputs[i]:
				index = i
				print("Found output device:", outputs[i])
				break
	midi_output = outputs[index]
	print("Connecting to output " + midi_output)
	port = mido.open_output(midi_output)
	ports_out.append(port)

# start ui thread
ui_thread = threading.Thread(target=update_ui)
ui_thread.start()

# connect midi devices
m = mpk.Akai_MPK_Mini()
m.send_RAM()
show_all()
connect_input(match="MPK")
connect_output(match="FLUID")
connect_output(match="TD-17")

print(ports_in)
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
