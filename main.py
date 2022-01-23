import mido
import time

inputs = mido.get_input_names()
ports = []


def connect_all():
	for midi_input in inputs:
		print("Connecting to " + midi_input)
		port = mido.open_input(midi_input)
		ports.append(port)

def connect_device(index):
	midi_input = inputs[index]
	print("Connecting to " + midi_input)
	port = mido.open_input(midi_input)
	ports.append(port)

connect_device(1)
for port, msg in mido.ports.multi_receive(ports, yield_ports=True):
	print(port, msg)