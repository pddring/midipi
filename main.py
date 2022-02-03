import socket
import mido
import time
import threading
import os
from screen import ScreenController
import mpk
from PIL import Image

s = ScreenController()

inputs = mido.get_input_names()
outputs = mido.get_output_names()
ports_in = []
ports_out = []
program_selected = 1
reverb_size = 0

# called in UI thread
def update_ui():
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

	# connect to fluidsynth
	tcp = socket.socket()
	tcp.connect(("localhost", 9800))
	tcp.send("set synth.nreverb.active 1\n".encode())
	
	
	t = 0
	while True:
		group = program_selected // 8
		s.image = images[group % len(images)]
		d = s.get_drawing()
		d.rectangle((0,0, 128, 20), fill=(255,255,255,255))
		s.print(str(program_selected) + ": " + programs[program_selected], fill=(0,0,0,255),update=False)
		s.print("Reverb: " + str(round(reverb_size, 2)), pos=(0, 10), fill=(0,0,0,255))
		
		if previous_values["reverb_size"] != reverb_size:
			m = "set synth.reverb.room-size " + str(round(reverb_size,2)) + "\n"
			print(m)
			tcp.send(m.encode())
			previous_values["reverb_size"] = reverb_size
		
		buttons = s.get_buttons()
		if "middle" in buttons:
			os.system("sudo shutdown -h now")

		time.sleep(.1)
		


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

for port, msg in mido.ports.multi_receive(ports_in, yield_ports=True):
	if msg.type=="note_on":
		print("Note on:", msg.note, msg.channel, msg.velocity)
	elif msg.type=="note_off":
		print("Note off:",msg.note, msg.channel, msg.velocity)
	elif msg.type=="control_change":
		print("Control change: ", msg)
		if msg.control==3:
			m = mido.Message("program_change", program=msg.value, channel=msg.channel)
			program_selected = msg.value
			for p in  ports_out:
				p.send(m)
		
		# reverb room size
		if msg.control==4:
			reverb_size = msg.value / 127
	else:
		print(msg)
	for p in ports_out:
		p.send(msg)
	#s.show_status()
