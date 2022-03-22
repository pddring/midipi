import mido
import re
import multiprocessing
import time
MATCH_INDEX = 0
MATCH_REGEX = 1
MATCH_NAME = 2

class MidiEngine:

    def listen_one(self, name):
        if not self.quiet_mode:
            print("Connecting to", name, "to listen (blocking)")
        input = mido.open_input(name)
        outputs = []
        if not self.quiet_mode:
            print("Connecting to outputs", self.connected_outputs)
        for o_name in self.connected_outputs:
            o = mido.open_output(o_name)
            outputs.append(o)

        while True:
            msg = input.receive()
            
            if msg.type=="control_change":
                if not self.quiet_mode:
                    print("Control change: ", msg)
                if msg.control==3:
                    m = mido.Message("program_change", program=msg.value, channel=msg.channel)
                    for o in outputs:
                        o.send(m)
            if msg.type == "program_change" and msg.channel == 9:
                msg.channel = 0
                if not self.quiet_mode:
                    print("Remapping program change from channel 10 to channel 1")
                    

            self.midi_pipe.send(msg)
            for o in outputs:
                o.send(msg)
    
    def change_program(self, program, channel=0):
        for o_name in self.connected_outputs:
            o = mido.open_output(o_name)
            msg = mido.Message("program_change", program=program, channel=channel)
            o.send(msg)
            o.close()

    def listen_all(self):
        for name in self.connected_inputs:
            t = multiprocessing.Process(target=self.listen_one, args=(name,), daemon=True)
            self._listen_threads.append(t)
            t.start()

    def stop(self):
        for t in self._listen_threads:
            t.terminate()
        self._listen_threads = []

    def reconnect(self):
        self.stop()
        self.listen_all()
    

    def scan(self):
        self.available_inputs = mido.get_input_names()
        self.available_outputs = mido.get_output_names()
        self.connected_inputs = []
        self.connected_outputs = []

    def __init__(self, quiet_mode=False, ):
        self.scan()
        self.quiet_mode=quiet_mode
        self.ui_pipe, self.midi_pipe = multiprocessing.Pipe()
        self._listen_threads = []
        
    def disconnect_output(self, device):
        if device in self.connected_outputs:
            if not self.quiet_mode:
                print("Disconnecting from output", device)
            self.connected_outputs.remove(device)
        else:
            if not self.quiet_mode:
                print("Cannot disconnect from", device, "(not connected in the first place)")

    def disconnect_input(self, device):
        if device in self.connected_inputs:
            if not self.quiet_mode:
                print("Disconnecting from input", device)
            self.connected_inputs.remove(device)
        else:
            if not self.quiet_mode:
                print("Cannot disconnect from", device, "(not connected in the first place)")

    def connect_input(self, device="", method=MATCH_NAME):
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

    def connect_output(self, device="", method=MATCH_NAME):
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
    m.connect_input(0, method=MATCH_INDEX)
    m.connect_output(0, method = MATCH_INDEX)
    print(m.connected_inputs, m.connected_outputs)
    m.listen_all()
    input("Press enter to quit")
    m.stop()
    
