#!/usr/bin/env python3
from __future__ import division
from custom_parser import *
import queue
import sys
from chromagram import compute_chroma
import numpy as np
import sounddevice as sd

q = queue.Queue()


def audio_callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    # Fancy indexing with mapping creates a (necessary!) copy:
    q.put(indata[::args.downsample, mapping])


def detect_chord(fs):
    global datastream
    while True:
        try:
            data = q.get_nowait()
        except queue.Empty:
            break
        shift = len(data)
        datastream = np.roll(datastream, -shift, axis=0)
        datastream[-shift:, :] = data


    # # compute PCP
    # chroma = compute_chroma(datastream, fs)
    # if np.all(chroma[:, n] == 0):
    #     chroma[:, n] = np.finfo(float).eps
    # else:
    #     chroma[:, n] /= np.max(np.absolute(chroma[:, n]))
    #
    # # get max probability path from Viterbi algorithm
    # (PI, A, B) = initialize(chroma, templates, nested_cof)
    # (path, states) = viterbi(PI, A, B)
    #
    # # normalize path
    # #         path[:, i] /= sum(path[:, i])
    #
    # # choose most likely chord - with max value in 'path'
    # final_chords = []
    # indices = np.argmax(path, axis=0)
    #
    # # find no chord zone
    # set_zero = np.where(np.max(path, axis=0) < 0.3 * np.max(path))[0]
    # if np.size(set_zero) is not 0:
    #     indices[set_zero] = -1
    #
    # # identify chords
    # if indices[i] == -1:
    #     final_chords.append('NC')
    # else:
    #     final_states[i] = states[indices[i], i]
    #     final_chords.append(chords[int(final_states[i])])
    #
    # print('Time(s)', 'Chords')
    # print(timestamp[i], final_chords[i])
        return 'A'


try:
    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, 'input')
        args.samplerate = device_info['default_samplerate']

    length = int(args.window * args.samplerate / args.downsample)

    stream = sd.InputStream(device=args.device, channels=max(args.channels),
                            samplerate=args.samplerate, callback=audio_callback)
    chord = detect_chord(fs=args.samplerate)
    with stream:
        print('Ciao')
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
