#!/usr/bin/python

# Single block audio FFT processing
# It does FFT to the whole audio, multiplies the amplitude/phase and do the IFFT for the whole spectrum
#
# You can use this to convolve signals and to get interesting effects.
# Usage: "./2xphases.py --help" for more information
# For loading non-wav files (like mp3, ogg, etc) or changing the samplerate it requires "avconv"
#
# You can try this for a whole melody to get interesting effect.

# by Nasca Octavian PAUL, Targu Mures, Romania
# http://www.paulnasca.com/

# this file is released under Public Domain

import sys
import gc
import warnings
import contextlib
import struct
import os
import os.path
import subprocess
import tempfile

import scipy.io.wavfile
import wave

import numpy as np
import matplotlib.pyplot as plt

from optparse import OptionParser
from tempfile import TemporaryFile

class Object:
    pass

def cleanup_memory():
    gc.collect()

def get_wave_file_info(input_filename):
    with contextlib.closing(wave.open(input_filename,'r')) as f:
        nsamples=f.getnframes()
        samplerate=f.getframerate()
        nchannels=f.getnchannels()

        info=Object()
        info.nsamples=nsamples
        info.samplerate=samplerate
        info.nchannels=nchannels
        return info


def read_wave_file(input_filename,nchannel):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        (samplerate,smp)=scipy.io.wavfile.read(input_filename)
        if len(smp.shape)==2:
            smp=smp[:,nchannel % smp.shape[1]]
        smp=np.float32(smp)
        smp=smp/32768.0
        cleanup_memory()
        return smp

def optimize_fft_size(n):
    orig_n=n
    while True:
        n=orig_n
        while (n%2)==0:
            n/=2
        while (n%3)==0:
            n/=3
        if n<2:
            break
        orig_n+=1
    return orig_n

def compute_resulted_file_info(input_filename_list,extra_seconds=0.0):
    result=Object()
    result.nsamples=0
    result.nchannels=1
    result.samplerate=0
    for input_filename in input_filename_list:
        info=get_wave_file_info(input_filename)
        result.nsamples=max(result.nsamples,info.nsamples)
        result.nchannels=max(result.nchannels,info.nchannels)
        if result.samplerate==0:
            result.samplerate=info.samplerate

    result.nsamples=optimize_fft_size(result.nsamples+int(result.samplerate*extra_seconds))

    return result

def fft_file_and_process(input_filename,nchannel,size_adjust,unwrap_phases):
    smp=read_wave_file(input_filename,nchannel)
    smp.resize(size_adjust)
    freqs=np.fft.rfft(smp)
    
    #get amplitude spectrum and phase spectrum
    freqs_amp=np.abs(freqs)
    freqs_amp*=1.0/(max(freqs_amp)+1e-6)
    freqs_phases=np.angle(freqs)

    if unwrap_phases!=0:
        freqs_phases=np.unwrap(freqs_phases)

    del smp
    del freqs
    cleanup_memory()

    freqs_amp_file = TemporaryFile()
    freqs_phases_file = TemporaryFile()

    np.save(freqs_amp_file,freqs_amp)
    np.save(freqs_phases_file,freqs_phases)
    freqs_amp_file.seek(0)
    freqs_phases_file.seek(0)
    
    files_freqs=Object()
    files_freqs.amp=freqs_amp_file
    files_freqs.phases=freqs_phases_file

    del freqs_amp
    del freqs_phases
    cleanup_memory()
    
    return files_freqs




def process_files(input_filename_list,options):
    info=compute_resulted_file_info(input_filename_list,options.extra_seconds)
    print "Resulted samples: ",info.nsamples
    print 
    file_result_smp_list=[]
    
    for nchannel in range(info.nchannels):
        cleanup_memory()
        file_freqs_list=[]

        #do FFT for input files
        for k,input_filename in enumerate(input_filename_list):
            print "Processing (ch: {0}/{1}) file #{2}" .format(nchannel+1,info.nchannels,k+1)
            file_freqs=fft_file_and_process(input_filename, nchannel,info.nsamples,options.unwrap_phases)
            file_freqs_list.append(file_freqs)

        #combine FFTs
        result_freqs_amp=None
        result_freqs_phases=None
        for file_freqs in file_freqs_list:
            if result_freqs_amp is not None:
                result_freqs_amp*=np.load(file_freqs.amp)
                result_freqs_phases+=np.load(file_freqs.phases)
            else:
                result_freqs_amp=np.load(file_freqs.amp)
                result_freqs_phases=np.load(file_freqs.phases)

            file_freqs.amp.close()
            file_freqs.phases.close()
            cleanup_memory()
   
        #do the processing

        #divide_by_nfiles=1.0/len(input_filename_list)
        divide_by_nfiles=1.0

        result_freqs_amp=np.power(result_freqs_amp,options.amplitude_power*divide_by_nfiles)
        result_freqs_phases=result_freqs_phases*options.phase_multiplier*divide_by_nfiles

        #remove low frequencies below 20Hz 
        i20Hz=int(20.0*info.nsamples/info.samplerate)
        result_freqs_amp[0:i20Hz]=0.0

        #convert to complex numbers
        result_freqs=result_freqs_amp*np.exp(1j*result_freqs_phases)

        del result_freqs_amp
        del result_freqs_phases
        cleanup_memory()

        #do ifft and normalize
        result_smp=np.fft.irfft(result_freqs)
        result_smp=result_smp/(max(np.abs(result_smp))+1e-6)
        
        result_smp_file=TemporaryFile()
        np.save(result_smp_file,result_smp)
        result_smp_file.seek(0)
        file_result_smp_list.append(result_smp_file)

        del result_freqs
        del result_smp
        cleanup_memory()

    #combine the outputs to audio (load the files)
    result_channels_smp=[]
    for file_result_smp in file_result_smp_list:
        smp=np.load(file_result_smp)
        result_channels_smp.append(np.int16(32767.0*(smp/(smp.max()+1e-6))))

    result_smp=np.dstack(result_channels_smp)[0]

    #save the output audio
    scipy.io.wavfile.write(options.output,info.samplerate,result_smp)



print "by Nasca Octavian PAUL, Targu Mures, Romania\n"
parser = OptionParser(usage="usage: %prog [options] -o output_wav input1 [input2...]")
parser.add_option("-a", "--amplitude_power", dest="amplitude_power",help="amplitude power (1.0 = no change)",type="float",default=1.0)
parser.add_option("-p", "--phase_multiplier", dest="phase_multiplier",help="phase multiplier (1.0 = no change)",type="float",default=1.0)
parser.add_option("-u", "--unwrap_phases", dest="unwrap_phases",help="unwrap phases (0=no,1=yes, default 1)",type="int",default=1)
parser.add_option("-r", "--sample_rate", dest="sample_rate",help="convert to samplerate",type="int",default=0)
parser.add_option("-s", "--extra_seconds", dest="extra_seconds",help="minimum amount silence appended",type="float",default=0.0)
parser.add_option("-o", "--output", dest="output",help="output WAV file",type="string",default="")
(options, args) = parser.parse_args()

if (len(args)<1) or (options.amplitude_power<0.0) or (options.output==""):
    print "Error in command line parameters. Run this program with --help for help."
    sys.exit(1)


input_filename_list=args[:]
print "Input files: "+", ".join(input_filename_list)
print "Output file: "+options.output
print

#convert the input files, if necessary

tmp_filename_list=[]

for k,input_filename in enumerate(input_filename_list):
    if options.sample_rate>0 or not os.path.splitext(input_filename)[1].lower()==".wav":
        tmp_file, tmp_filename = tempfile.mkstemp(prefix="2xphases_",suffix=".wav")
        os.close(tmp_file)
        tmp_filename_list.append(tmp_filename)
        input_filename_list[k]=tmp_filename
    
        cmdline=["avconv", "-y", "-v","quiet", "-i",input_filename]
        if options.sample_rate>0:
                cmdline+=["-ar",str(options.sample_rate)]
        cmdline.append(tmp_filename)
        subprocess.call(cmdline)



process_files(input_filename_list,options)

#cleanup temp files
for tmp_filename in tmp_filename_list:
    os.remove(tmp_filename)


