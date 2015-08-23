audio processing using autoconvolution
======================================

by Nasca Octavian Paul
http://www.paulnasca.com

This is an experimental audio effect which is based on autoconvolution. The idea is to take the input audio and convolve it with itself. 

Using simple auto-convolution has two drawbacks:
 - stronger frequencies are amplified more (because the magnitudes are squared)
 - all notes tends to appear all over the place (over the length of resulting audio, resulting a dissonant mix)

In order to minimize these drawbacks I am using these ideas:
 - extract the frequency envelope from the input signal, do the autoconvolution of the whitened signal and apply the extracted envelope. By doing this the overall magnitudes of the input signal are preserved.
 - use partitioned autoconvolution (by dividing the signal into blocks) and limiting the number of adjacent blocks (partitions) which are used in convolution. This also reduces the memory usage allowing using this effect on very long audio.

Here are some examples using one minute excerpts from different songs:
 1. using [Believe In You - Dash Berlin feat. Sarah Howells Secede](https://www.youtube.com/watch?v=aCanu-ruBbI)
   - [simple autoconvolution](audio_demos/1_full_k1.ogg?raw=true), this is the simple autoconvolution; notice that the most frequencies are damped and all notes appear all over the places
   - [simple autoconvolution envelope preservation](audio_demos/1_full_k2.ogg?raw=true), this is the simple autoconvolution too but the overall frequency envelope is preserved; much better than the previous one but still, all notes appear all over the places
  
  The next demos are made using partitioned autoconvolution where the spread of the signal is limited and the overall frequency envelope is preserved.

   - [limiting the spread to 1 second](audio_demos/1_spread_1_second.ogg?raw=true); the spread is limited to 1 seconds
   - [limiting the spread to 5 seconds](audio_demos/1_spread_5_seconds.ogg?raw=true); the spread is limited to 5 seconds
  
 
 2. using [Era - Tara Shahti Mantra](https://www.youtube.com/watch?v=EAZd6LFME9A)
  - [limiting the spread to 15 seconds](audio_demos/2_spread_15_seconds.ogg?raw=true); 
  - [limiting the spread to 3 seconds](audio_demos/2_spread_3_seconds.ogg?raw=true); 
  - [limiting the spread to half second](audio_demos/2_spread_half_second.ogg?raw=true); notice that if the spread is too low (less than one second) it sounds more like a 2x sound stretch
 
 3. using [Enya - Athair Ar Neamh](https://www.youtube.com/watch?v=JIABga915AY)
  - [limiting the spread to 15 seconds](audio_demos/3_spread_15_seconds_keep_envelope.ogg?raw=true); 
  - [limiting the spread to 3 seconds](audio_demos/3_spread_3_seconds_keep_envelope.ogg?raw=true); 
  - [limiting the spread to 15 seconds without envelope preservation](audio_demos/3_spread_15_seconds.ogg?raw=true); 
  - [limiting the spread to 3 seconds without envelope preservation](audio_demos/3_spread_3_seconds.ogg?raw=true); 


More processed songs with this effect are available at [mixcloud](https://www.mixcloud.com/2xphases/).

To run this software you need Python with Scipy installed.
For command-line options, run "autoconvolution.py --help".

The most important commandline options are:
 - "-k" - preserve frequency envelope 
 - "-K" - two aligned files are generated: one w/o envelope preservation and the other with frequency envelope preservation. These can be mixed using Audacity or any audio mixer.

 - the spread limiting is set by multiplying the "block size" ("-b") with "limit blocks" ("-l"); 
  example for :
 *autoconvolution.py -b 5 -l 3 -k -o output.wav input.mp3*
 This sets the block size to 5 seconds and limit blocks to 3 so the spread is 5**3=15 seconds.
 

You can read the .py source code for more details :)



