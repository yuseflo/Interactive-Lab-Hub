arecord -D hw:2,0 -f cd -c1 -r 44100 -d 5 -t wav recorded_mono.wav
python3 main.py recorded_mono.wav
