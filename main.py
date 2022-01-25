import mido
import time
from screen import ScreenController

s = ScreenController()

inputs = mido.get_input_names()
outputs = mido.get_output_names()
ports_in = []
ports_out = []


def connect_all():
	for midi_input in inputs:
		print("Connecting to input" + midi_input)
		port = mido.open_input(midi_input)
		ports_in.append(port)
	for midi_output in outputs:
		print("Connecting to output" + midi_output)
		port = mido.open_output(midi_output)
		ports_out.append(port)

def connect_input(index):
	midi_input = inputs[index]
	print("Connecting to " + midi_input)
	port = mido.open_input(midi_input)
	ports_in.append(port)

def connect_output(index):
	midi_output = outputs[index]
	print("Connecting to output " + midi_output)
	port = mido.open_output(midi_output)
	ports_out.append(port)

connect_input(1)
connect_output(-1)
s.load_image("keys.png")
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
