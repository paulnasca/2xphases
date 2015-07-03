#!/usr/bin/python
#
# Autoconvolution for long audio files
#
# The autoconvolution can produce very interesting effects on audio (especially if the overall spectrum envelope is preserved)
# For loading non-wav files (like mp3, ogg, etc) or changing the samplerate it requires "avconv"
# This software requires a lot of temporary hard drive space for processing 
#
# You can try this for a whole melody to get interesting effect.
#
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
import glob
from collections import defaultdict

from scipy import signal,ndimage
import wave
import scipy.io.wavfile #temporary

import numpy as np

from optparse import OptionParser
from tempfile import TemporaryFile

tmpextension=".npy"

def print_self_memory_usage(text):
    cleanup_memory()
    with open("/proc/self/status") as f:
        content = f.readlines()
        for l in content:
            if l.startswith("VmData"):
                print text+" "+l.strip()


def cleanup_memory():
    gc.collect()

def get_tmpfft_filename(tmpdir,block_k,nchannel):
    return os.path.join(tmpdir,"tmpfft_%d_%d" % (block_k,nchannel)+tmpextension)

def get_tmpsmp_filename(tmpdir,block_k):
    return os.path.join(tmpdir,"tmpsmp_%d" % (block_k)+tmpextension)


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

def get_block_mixes(n_blocks):
    pos=defaultdict(lambda:{})
    
    for j in range(n_blocks):
        for i in range(n_blocks):
            val=(min(i,j),max(i,j))
            if val not in pos[i+j]:
                pos[i+j][val]=0
            pos[i+j][val]+=1
    result=[v for k,v in pos.iteritems()]
    return result

def process_audiofile(input_filename,output_filename,options):
    tmpdir=tempfile.mkdtemp("2xautoconvolution")
   
    cmdline=["avconv", "-y", "-v","quiet", "-i",input_filename]
    tmp_wav_filename=os.path.join(tmpdir,"tmp_input.wav")
    cmdline.append(tmp_wav_filename)
    subprocess.call(cmdline)

    envelopes=None
    samplerate=0
    with contextlib.closing(wave.open(tmp_wav_filename,'rb')) as f:
        samplerate=f.getframerate()
    input_block_size_samples=int(optimize_fft_size(options.blocksize_seconds*samplerate))
    print "Input block size (samples):",input_block_size_samples
    if options.keep_envelope:
        print "Spectrum envelope preservation: enabled"
        envelopes=[]
        output_block_size_samples=optimize_fft_size(int(input_block_size_samples*2.5))
    else:
        output_block_size_samples=input_block_size_samples*2
    
    extra_output_samples=output_block_size_samples-input_block_size_samples*2

    nchannels=0

    fft_size=output_block_size_samples/2+1

    #read 16 bit wave files
    with contextlib.closing(wave.open(tmp_wav_filename,'rb')) as f:
        nsamples=f.getnframes()
        nchannels=f.getnchannels()

        if envelopes is not None:
            for nchannel in range(nchannels):
                envelopes.append(np.zeros(fft_size,dtype=np.float32))

        
        n_blocks=nsamples//input_block_size_samples+1

        #force adding extra zero block to flush out all the samples
        n_blocks+=1

        print "Using %d blocks" % n_blocks
        #analyse audio and make frequency blocks
        for block_k in range(n_blocks):
            print "Doing FFT for block %d/%d" % (block_k+1,n_blocks)
            inbuf=f.readframes(input_block_size_samples)
            freq_block=[]
            for nchannel in range(nchannels):
                smp=np.fromstring(inbuf,dtype=np.int16)[nchannel::nchannels]

                smp=smp*np.float32(1.0/32768)
                smp=np.concatenate((smp,np.zeros(output_block_size_samples-len(smp),dtype=np.float32)))
                in_freqs=np.complex64(np.fft.rfft(smp))
                tmp_filename=get_tmpfft_filename(tmpdir,block_k,nchannel)

                if envelopes is not None:
                    envelopes[nchannel]+=np.abs(in_freqs)
                np.save(tmp_filename,in_freqs)

                del in_freqs
                del smp

                cleanup_memory()
            del inbuf
        cleanup_memory()
        
    
    #smooth envelopes
    if envelopes is not None:
        print "Smoothing envelopes"
        for nchannel in range(nchannels):
            one_hz_size=2.0*float(fft_size)/float(samplerate)
            envelopes[nchannel]=ndimage.filters.maximum_filter1d(envelopes[nchannel],size=int(one_hz_size+0.5))+1e-9
    
    #get the freq blocks and combine them, saving each output chunk
    block_mixes=get_block_mixes(n_blocks)
   
    max_smp=np.zeros(nchannels,dtype=np.float32)+1e-6
    for k,block_mix in enumerate(block_mixes):
        print "Mixing blocks %d/%d " % (k+1,len(block_mixes))
        multichannel_smps=[]
        for nchannel in range(nchannels): 
            sum_freqs=np.zeros(output_block_size_samples/2+1,dtype=np.complex64)
            for ((b1_k,b2_k),mul) in block_mix.iteritems():
                #if abs(b1_k-b2_k)>2: continue #interesting effect
                freq1=np.load(get_tmpfft_filename(tmpdir,b1_k,nchannel))
                freq2=np.load(get_tmpfft_filename(tmpdir,b2_k,nchannel))
                sum_freqs+=(freq1*freq2)*mul
                cleanup_memory()
            if envelopes is not None:
                sum_freqs=sum_freqs/envelopes[nchannel]
            smp=np.float32(np.fft.irfft(sum_freqs))
            cleanup_memory()
            if extra_output_samples>0:
                extra=extra_output_samples/2
                smp=np.roll(smp,extra)
                smp[:extra]*=np.linspace(0.0,1.0,extra)
                smp[-extra:]*=np.linspace(1.0,0.0,extra)
                cleanup_memory()
            del sum_freqs
            max_current_smp=max(np.amax(smp),-np.amin(smp))
            max_smp[nchannel]=max(max_current_smp,max_smp[nchannel])
            multichannel_smps.append(smp)
            del smp
            cleanup_memory()
        multichannel_smps=np.dstack(multichannel_smps)[0]
        np.save(get_tmpsmp_filename(tmpdir,k),multichannel_smps)
        del multichannel_smps
        cleanup_memory()
#tes

    print "Combining blocks"
    #get the output chunks, normalize them and combine to one wav file
    with contextlib.closing(wave.open(output_filename,'wb')) as f:
        f.setnchannels(nchannels)
        f.setframerate(samplerate)
        f.setsampwidth(2)
        
        old_buf=[]
        for k in range(len(block_mixes)):
            print "Output block %d/%d" % (k+1,len(block_mixes))
            current_smps=np.float32(np.load(get_tmpsmp_filename(tmpdir,k))*(0.7/max_smp))
            current_buf=current_smps[:input_block_size_samples]
            result_buf=current_buf
                 
            old_buf=[o for o in old_buf if o.shape[0]>=input_block_size_samples]
            for oldk,old in enumerate(old_buf):
                result_buf+=old[:input_block_size_samples]
                old_buf[oldk]=old[input_block_size_samples:]
            old_buf.append(current_smps[input_block_size_samples:])

            output_buf=np.int16(result_buf*32767.0).flatten().tostring()
            f.writeframes(output_buf)

            del result_buf
            del current_smps
            del current_buf
            del output_buf
            cleanup_memory()



    #cleanup
    for fn in glob.glob(os.path.join(tmpdir,"*"+tmpextension)):
        os.remove(fn)
    os.remove(tmp_wav_filename)
    try:
        os.rmdir(tmpdir)
    except OSError:
        pass




parser = OptionParser(usage="usage: %prog [options] -o output.wav input.wav")
parser.add_option("-o", "--output", dest="output",help="output WAV file",type="string",default="")
parser.add_option("-k", "--keep-envelope", dest="keep_envelope", action="store_true",help="try to preserve the overall amplitude envelope",default=False)
parser.add_option("-b", "--blocksize_seconds", dest="blocksize_seconds",help="blocksize (seconds)",type="float",default=60.0)
(options, args) = parser.parse_args()

if len(args)!=1 or len(options.output)==0:
    print "Error in command line parameters. Run this program with --help for help."
    sys.exit(1)

input_filename=args[0]
print "Input file: "+input_filename
print "Output file: "+options.output
if not os.path.isfile(input_filename):
    print "Error: Could not open input file:",input_filename
    sys.exit(1)
process_audiofile(input_filename,options.output,options)




