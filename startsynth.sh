sudo killall fluidsynth
killall python
sudo fluidsynth  -si -r22050 -c8 -z64 --audio-driver=alsa --gain 3 /usr/share/sounds/sf2/FluidR3_GM.sf2 &
python main.py &
