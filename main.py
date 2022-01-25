import mido
import time
import threading
from screen import ScreenController

s = ScreenController()

inputs = mido.get_input_names()
outputs = mido.get_output_names()
ports_in = []
ports_out = []

def update_ui():
	s.load_image("keys.png")
	d = s.get_drawing()
	t = 0
	while True:
		s.print(str(t), fill=(0,0,0,255))
		t += 1
		time.sleep(1)
		d.rectangle((0,0, 128, 10), fill=(255,255,255,255))


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

ui_thread = threading.Thread(target=update_ui)
ui_thread.start()
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
			print(m)
			for p in  ports_out:
				p.send(m)
	else:
		print(msg)
	for p in ports_out:
		p.send(msg)
	#s.show_status()
