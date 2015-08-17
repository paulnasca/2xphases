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
 1. original: [Believe In You - Dash Berlin feat. Sarah Howells Secede](https://www.youtube.com/watch?v=aCanu-ruBbI)
 
 2. original: [Era - Tara Shahti Mantra](https://www.youtube.com/watch?v=EAZd6LFME9A)
 
 3. original: [Enya - Athair Ar Neamh](https://www.youtube.com/watch?v=JIABga915AY)



autoconvolution.py -b 20 -k -o output.wav input.mp3

Read the .py files for more details.



