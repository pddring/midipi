#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# MPK M2-editor
# No-UI module
# Copyright (C) 2017  Damien Picard dam.pic AT free.fr
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# TODO
## get programmes
## send programmes
##     single
##     all
# get ram
## send ram
## interface
##     tabs for progs
##     autofill
## load/save config
#     single program
#     multi  programs
##     .mk2
#     mk1
#     human readable
# live update
# factory reset
# package
# PyPI?

import sys
import os
import rtmidi
import time
from collections import OrderedDict
from pprint import pprint




class Akai_MPK_Mini():

    GET_CONFIG = [240, 71, 0, 38, 102, 0, 1, 1, 247]

    def __init__(self):
        self.midi_config = OrderedDict((
            ("sysex_0", 240),  # [240]
            ("sysex_1", 71),  # [71]
            ("sysex_2", 0),  # [0]
            ("sysex_3", 38),  # [38]
            ("sysex_4", 103),  # [103] send 100; RAM 102
            ("sysex_5", 0),  # [0] get RAM 1
            ("sysex_6", 109),  # [109]

            ("programme", 1),  # [1,4]

            ("pad_channel", 9),  # [0,15]
            ("key_channel", 0),  # [0,15]

            ("key_octave", 4),  # [0,8] (-4,4)

            ("arp_on", 0),  # [0=OFF; 1=ON] no effect on programmes...?
            ("arp_mode", 0),  # [0=UP; 1=DOWN; 2=EXCLUSIVE; 3=INCLUSIVE; 4=ORDER; 5=RANDOM]
            ("arp_time", 5),  # div [0=1/4; 1=1/4T;  2=1/8;  3=1/8T;  4=1/16;  5=1/16T;  6=1/32;  7=1/32T]
            ("arp_clock", 0),  # [0=INTERNAL; 1=EXTERNAL]
            ("arp_latch", 0),  # [0=OFF; 1=ON]
            ("arp_swing", 0),  # [0=50%; 1=55%; 2=57%; 3=59%; 4=61%; 5=64%]
            ("arp_taps", 3),  # [2,4]

            # The arpeggiator tempo is encoded using 2 bytes
            # the first one may be 0 or 1
            # if the first one is 0
            #    then the second one is in [30,127]
            # if the first one is 1
            #    then the second one is in [0,112] (128,240)
            ("arp_tempo_0", 0),  # 0 [0,1]
            ("arp_tempo_1", 79),  # 1 [30,127; 0,112]

            ("arp_octave", 1),  # [0,3]

            ("x_axis_type", 0),  # [0=PITCHBEND; 1=CC1; 2=CC2]
            ("x_axis_L", 80),  # [0,127]
            ("x_axis_R", 81),  # [0,127]

            ("y_axis_type", 1),
            ("y_axis_D", 83),
            ("y_axis_U", 82),

            # Bank A
            ("b1_p1_NT", 35),  # [0,127]
            ("b1_p1_PC", 56),  # [0,127]
            ("b1_p1_CC", 31),  # [0,127]
            ("b1_p1_TP", 1),  # [0=TOGGLE; 1=MOMENTARY]

            ("b1_p2_NT", 38),
            ("b1_p2_PC", 124),
            ("b1_p2_CC", 32),
            ("b1_p2_TP", 1),

            ("b1_p3_NT", 42),
            ("b1_p3_PC", 123),
            ("b1_p3_CC", 33),
            ("b1_p3_TP", 1),

            ("b1_p4_NT", 51),
            ("b1_p4_PC", 118),
            ("b1_p4_CC", 34),
            ("b1_p4_TP", 1),

            ("b1_p5_NT", 46),
            ("b1_p5_PC", 110),
            ("b1_p5_CC", 35),
            ("b1_p5_TP", 1),

            ("b1_p6_NT", 49),
            ("b1_p6_PC", 90),
            ("b1_p6_CC", 36),
            ("b1_p6_TP", 1),

            ("b1_p7_NT", 45),
            ("b1_p7_PC", 87),
            ("b1_p7_CC", 37),
            ("b1_p7_TP", 1),

            ("b1_p8_NT", 47),
            ("b1_p8_PC", 0),
            ("b1_p8_CC", 38),
            ("b1_p8_TP", 1),

            # Bank B
            ("b2_p1_NT", 8),
            ("b2_p1_PC", 23),
            ("b2_p1_CC", 39),
            ("b2_p1_TP", 0),

            ("b2_p2_NT", 9),
            ("b2_p2_PC", 24),
            ("b2_p2_CC", 40),
            ("b2_p2_TP", 0),

            ("b2_p3_NT", 10),
            ("b2_p3_PC", 25),
            ("b2_p3_CC", 41),
            ("b2_p3_TP", 0),

            ("b2_p4_NT", 11),
            ("b2_p4_PC", 26),
            ("b2_p4_CC", 42),
            ("b2_p4_TP", 0),

            ("b2_p5_NT", 12),
            ("b2_p5_PC", 27),
            ("b2_p5_CC", 43),
            ("b2_p5_TP", 0),

            ("b2_p6_NT", 13),
            ("b2_p6_PC", 28),
            ("b2_p6_CC", 44),
            ("b2_p6_TP", 0),

            ("b2_p7_NT", 14),
            ("b2_p7_PC", 29),
            ("b2_p7_CC", 45),
            ("b2_p7_TP", 0),

            ("b2_p8_NT", 15),
            ("b2_p8_PC", 30),
            ("b2_p8_CC", 46),
            ("b2_p8_TP", 0),

            # Knobs
            ("k1_CC", 1),  # [0,127]
            ("k1_LO", 0),  # [0,127]
            ("k1_HI", 127),  # [0,127]

            ("k2_CC", 2),
            ("k2_LO", 0),
            ("k2_HI", 127),

            ("k3_CC", 3),
            ("k3_LO", 0),
            ("k3_HI", 127),

            ("k4_CC", 91),
            ("k4_LO", 0),
            ("k4_HI", 127),

            ("k5_CC", 5),
            ("k5_LO", 0),
            ("k5_HI", 127),

            ("k6_CC", 6),
            ("k6_LO", 0),
            ("k6_HI", 127),

            ("k7_CC", 7),
            ("k7_LO", 0),
            ("k7_HI", 127),

            ("k8_CC", 93),
            ("k8_LO", 0),
            ("k8_HI", 127),

            ("key_transpose", 3),  # [0,24]
            ("sysex_end", 247)  # [247]
            ))
        self.do_live_update = False
        self.controller_found = False
        self.midi_setup()

    def show_popup_controller_not_found(self):
        print("Controller not found")
    
    def rx(self, msg, data):
        d, time = msg
        h = [hex(i) for i in d]
        print(h, data)

    def midi_setup(self):
        self.mo = rtmidi.MidiOut()
        self.mi = rtmidi.MidiIn()

        is_out_open, is_in_open = False, False
        for i, p in enumerate(self.mo.get_ports()):
            if any(mpk in p for mpk in ("MPKmini", "MPK Mini")):
                self.mo.open_port(i)
                is_out_open = True
        for i, p in enumerate(self.mi.get_ports()):
            if any(mpk in p for mpk in ("MPKmini", "MPK Mini")):
                self.mi.open_port(i)
                self.mi.ignore_types(sysex=False)
                #self.mi.set_callback(self.rx)
                is_in_open = True

        if not is_out_open and not is_in_open:
            self.show_popup_controller_not_found()
        else:
            self.controller_found = True

    def send_midi_message(self, out_message, expected_msg=117):
        in_message = [[]]
        # print('out:', out_message)
        self.mo.send_message(out_message)
        time.sleep(0.1)

        # O Karnaugh, help me!
        while ((expected_msg is None
                and in_message is not None)
               or (expected_msg is not None
                   and (
                        in_message is None
                        or len(in_message[0]) == 0
                        or type(in_message) is tuple
                        and len(in_message[0]) != expected_msg
                        )
                   )
               ):
            in_message = self.mi.get_message()
            # print('in:', in_message)
        if in_message is not None:
            in_message = in_message[0]  # strip midi time
        return in_message

    def get_all_programmes(self):
        for p_i in range(1, 5):
            self.get_programme(p_i)

    def get_active_programme(self):
        p_i = self.get_active_tab_index()
        self.get_programme(p_i)

    def get_programme(self, p_i):
        out_message = self.GET_CONFIG[:]
        out_message[7] = p_i
        in_message = self.send_midi_message(out_message, 117)
        self.fill_tab(in_message, p_i)

    def copy_to(self, p_to):
        p_from = self.get_active_tab_index()
        conf = self.get_tab_programme(p_from)
        self.fill_tab(conf, p_to)

    def send_all_programmes(self):
        for p_i in range(4):
            self.send_programme(p_i)

    def send_active_programme(self):
        p_i = self.get_active_tab_index()
        self.send_programme(p_i)

    def send_programme(self, p_i):
        message = self.get_tab_programme(p_i)
        message[4] = 100
        self.send_midi_message(message, None)

    def get_RAM(self):
        p_i = self.get_active_tab_index()
        out_message = self.GET_CONFIG[:]
        out_message[5] = 0
        out_message[7] = 0
        print(out_message)
        in_message = self.send_midi_message(out_message, 117)
        print(in_message)
        self.fill_tab(in_message, p_i)


    def send_RAM(self):
        #p_i = self.get_active_tab_index()
        #out_message = self.get_tab_programme(p_i)
        out_message = list(self.midi_config.values())
        print(out_message)
        out_message[4] = 100
        out_message[7] = 0
        self.send_midi_message(out_message, None)

    # I/O
    def load_mk2(self, filepath):
        print('Loading', filepath)
        with open(filepath, 'rb') as f:
            conf = [int(i) for i in f.read()]
            # print(len(conf))
            self.fill_tab(conf, self.get_active_tab_index())

    def save_mk2(self, filepath):
        print('Saving', filepath)
        conf = self.get_tab_programme(self.get_active_tab_index())
        with open(filepath, 'wb') as f:
            for b in conf:
                f.write(b.to_bytes(1, 'little'))

    # Autofill
    def show_autofill(self):
        self.autofill_window.show()

if __name__ == "__main__":
    mpk = Akai_MPK_Mini()
    mpk.send_RAM()
    print(mpk.midi_config)
    while True:
        time.sleep(1)
