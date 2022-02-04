sudo killall fluidsynth
killall python
sudo fluidsynth  -si -r44100 -c8 -z64 --audio-driver=alsa --gain 1 /usr/share/sounds/sf2/FluidR3_GM.sf2 &
python main.py &
