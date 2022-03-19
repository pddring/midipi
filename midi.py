import mido
import re
MATCH_INDEX = 0
MATCH_REGEX = 1
MATCH_NAME = 2

class MidiEngine:
    

    def scan(self):
        self.available_inputs = mido.get_input_names()
        self.available_outputs = mido.get_output_names()
        self.connected_inputs = []
        self.connected_outputs = []

    def __init__(self):
        self.scan()

    def connect_input(self, device=0, method=MATCH_NAME):
        if method == MATCH_INDEX:
            i = device
            if i >= 0 and i < len(self.available_inputs):
                name = self.available_inputs[i]
                self.connect_input(name)
        
        elif method == MATCH_REGEX:
            for name in self.available_inputs:
                if re.search(device, name):
                    self.connect_input(name)

        elif method == MATCH_NAME:
            if device not in self.connected_inputs:
                if device in self.available_inputs:
                    self.connected_inputs.append(device)
                else:
                    raise Exception("MIDI input device not found: " + device)

    def connect_output(self, device=0, method=MATCH_NAME):
        if method == MATCH_INDEX:
            i = device
            if i >= 0 and i < len(self.available_outputs):
                name = self.available_outputs[i]
                self.connect_output(name)
        
        elif method == MATCH_REGEX:
            for name in self.available_outputs:
                if re.search(device, name):
                    self.connect_output(name)

        elif method == MATCH_NAME:
            if device not in self.connected_outputs:
                if device in self.available_outputs:
                    self.connected_outputs.append(device)
                else:
                    raise Exception("MIDI output device not found: " + device)

if __name__ == "__main__":
    m = MidiEngine()
    m.connect_input("T", MATCH_REGEX)
    m.connect_output(0, MATCH_INDEX)
    print(m.connected_inputs, m.connected_outputs)