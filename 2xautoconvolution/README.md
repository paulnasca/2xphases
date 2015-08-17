audio processing using autoconvolution
======================================

by Nasca Octavian Paul
http://www.paulnasca.com

This is an audio effect which is based on autoconvolution. The idea is to take the input audio and to convolve with itself. 

Using simple auto-convolution has two drawbacks:
 - the stronger input signals are amplified more (because the magnitudes are squared)
 - all notes tends toappear all over the place over the length of resulting audio (resulting a dissonant mix)

In order to minimize these drawbacks I am using two ideas:
 - extract the frequency envelope from the input signal, do the autoconvolution and apply the extracted envelope. By doing this the magnitude of the input signal are preserved.
 - use partitioned autoconvolution (by dividing the signal into blocks) and limiting the number of adjacent blocks which are used

Here are some examples using one minute excerpts from different songs:
 1. using [Believe In You - Dash Berlin feat. Sarah Howells Secede](https://www.youtube.com/watch?v=aCanu-ruBbI)
   - ![](audio_demos/1_full_k1.ogg?raw=true), this is the simple autoconvolution; notice that the most frequencies are damped and all notes appear all over the places
   - ![simple autoconvolution](audio_demos/1_full_k1.ogg?raw=true), this is the simple autoconvolution; notice that the most frequencies are damped and all notes appear all over the places
   - ![simple autoconvolution envelope preservation](audio_demos/1_full_k2.ogg?raw=true), this is the simple autoconvolution but the overall frequency envelope is preserved; much better than the previous one but still, all notes appear all over the places
  
  The next demos are made using partitioned autoconvolution where the spread of the signal is limited and the overall frequency envelope is preserved.

   - [limiting the spread to 1 second](audio_demos/1_spread_1_second.ogg?raw=true); the spread is limited to 1 seconds
   - [limiting the spread to 5 seconds](audio_demos/1_spread_5_seconds.ogg?raw=true); the spread is limited to 5 seconds
  
 
 2. using [Era - Tara Shahti Mantra](https://www.youtube.com/watch?v=EAZd6LFME9A)
  - [limiting the spread to 15 seconds](audio_demos/2_spread_15_seconds.ogg?raw=true); 
  - [limiting the spread to 3 seconds](audio_demos/2_spread_3_seconds.ogg?raw=true); 
  - [limiting the spread to half second](audio_demos/2_spread_half_second.ogg?raw=true); notice that if the spread is too low (less than one seconds) it sounds more like an extreme sound stretch
 
 3. using [Enya - Athair Ar Neamh](https://www.youtube.com/watch?v=JIABga915AY)
  - [limiting the spread to 15 seconds](audio_demos/3_spread_15_seconds_keep_envelope.ogg?raw=true); 
  - [limiting the spread to 3 seconds w/o envelope preservation](audio_demos/3_spread_3_seconds_keep_envelope.ogg?raw=true); 
  - [limiting the spread to 15 seconds](audio_demos/3_spread_15_seconds.ogg?raw=true); 
  - [limiting the spread to 3 seconds w/o envelope preservation](audio_demos/3_spread_3_seconds.ogg?raw=true); 



autoconvolution.py -b 20 -k -o output.wav input.mp3

Read the .py files for more details.



