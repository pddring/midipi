sudo killall fluidsynth
killall python3
sudo fluidsynth  -si -r44100 -c3 -z64 --audio-driver=alsa --gain 1 /usr/share/sounds/sf2/FluidR3_GM.sf2 -o alsa.device=plughw:IQaudIODAC &
python3 main.py &
