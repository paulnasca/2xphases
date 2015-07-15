oggdec in_*.ogg

./2xphases.py -s 10 -p 2.0 in_arpeggio.wav -o out_arpeggio2x.wav
./2xphases.py -s 10 -p 2.0 -a 1.3 in_librivox.wav -o out_librivox2x.wav
./2xphases.py -s 10 -p 1.1 in_librivox.wav -o out_librivox11x.wav
./2xphases.py -s 10 -a 0.7 in_arpeggio.wav in_librivox.wav -o out_convolution_arpeggio_librivox.wav
./2xphases.py -s 10 in_librivox.wav in_reverb.wav -o out_convolution_librivox_reverb.wav

#todo add 2xautoconvolution.py examples

